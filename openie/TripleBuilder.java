package openie;


import openie.*;

import java.io.File;
import java.io.FileWriter;
import java.io.FilenameFilter;
import java.io.FileNotFoundException;
import java.util.stream.Stream;
import java.util.Scanner;
import java.util.Collection;
import java.util.Properties;
import java.util.List;
import java.util.ArrayList;
import java.util.Optional;
import java.util.UUID;
import java.util.HashMap;
import java.util.Map;
import java.util.Arrays;
import static java.util.stream.Collectors.*;

import edu.stanford.nlp.ie.util.RelationTriple;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.CoreDocument;
import edu.stanford.nlp.pipeline.CoreEntityMention;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.naturalli.NaturalLogicAnnotations;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.ling.CoreLabel;

import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.BasicDependenciesAnnotation;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.semgraph.SemanticGraphEdge;
import edu.stanford.nlp.ling.IndexedWord;

import edu.stanford.nlp.coref.CorefCoreAnnotations;
import edu.stanford.nlp.coref.data.CorefChain;
import edu.stanford.nlp.coref.data.Mention;


public class TripleBuilder {

    public static void main(String[] args) throws Exception {
        // Create the Stanford CoreNLP pipeline
        Properties props = new Properties();
        // props.setProperty("openie.format", ""); // DOES NOT MAKE A DIFFERCE IN THIS APPLICATION.
        // props.setProperty("openie.filelist", ""); // DOES NOT MAKE A DIFFERCE IN THIS APPLICATION.
        // props.setProperty("openie.threads", ""); // DOES NOT MAKE A DIFFERCE IN THIS APPLICATION.
        props.setProperty("openie.max_entailments_per_clause", "100"); // DOES NOT SEEM TO REALLY MAKE A DIFFERENCE.
        props.setProperty("openie.resolve_coref", "true"); // VERY USEFUL!
        props.setProperty("openie.ignore_affinity", "true"); // WHEN TRUE, REMOVES TRIPLES THAT HAVE AFFINITY BELOW 1.0. MIGHT BE USEFUL COMBINED WITH THE affinity_probability_cap PROPERTY.
        props.setProperty("openie.affinity_probability_cap", "1.0"); // SETTING IT TO 1.0 LEAVES ALL AFFINITY VALUES UNROUNDED. MIGHT BE USEFUL COMBINED WITH THE ignore_affinity PROPERTY.
        // props.setProperty("openie.triple.strict", "false"); // WHEN FALSE, THE TRIPLES CHANGE SLIGHTLY.
        // props.setProperty("openie.triple.all_nominals", "true"); // WHEN TRUE, THE NUMBER OF TRIPLES INCREASES A SMALL AMOUNT. THE EXTRA TRIPLES DO NOT SEEM VERY USEFUL THOUGH, THEY ARE MOSTLY INDICATING ADJECTIVES.
        // props.setProperty("openie.splitter.model", ""); // WILL NOT BE USED.
        // props.setProperty("openie.splitter.nomodel", "true"); // DOES NOT CHANGE MUCH.
        // props.setProperty("openie.splitter.disable", "true"); // THIS IS AN IMPORTANT ONE. WHEN TRUE, THE NUMBER OF TRIPLES IS MINIMAL.
        // props.setProperty("openie.affinity_models", ""); // WILL NOT BE USED.
        props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner,depparse,coref,natlog,openie");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

        File folder = new File("documents/");
        FilenameFilter filter = new FilenameFilter() {
            @Override
            public boolean accept(File f, String name) {
                boolean isTXT = name.endsWith(".txt");
                boolean tripleExists = (new File("triples/" + name.replace(".txt", ".csv"))).exists();
                
                return isTXT && !tripleExists;
            }
        };
        File[] files = folder.listFiles(filter);

        for (File f : files) {
            try {
                Scanner reader = new Scanner(f, "utf-8");
                FileWriter writer = new FileWriter("triples/" + f.getName().replace(".txt", ".csv"));
                UUID uniqueId = UUID.randomUUID();
                String tripleText = Triple.getHeader(f.getAbsolutePath());

                while (reader.hasNextLine()) {
                    String line = reader.nextLine();
                    CoreDocument doc = new CoreDocument(line);
                    pipeline.annotate(doc);
                    List<CoreEntityMention> entityMentions = doc.entityMentions();

                    for (CoreMap sentence : doc.annotation().get(CoreAnnotations.SentencesAnnotation.class)) {
                        SemanticGraph graph = sentence.get(BasicDependenciesAnnotation.class);
                        Collection<RelationTriple> triples = sentence.get(NaturalLogicAnnotations.RelationTriplesAnnotation.class);
                        List<Entity> entities = getEntities(graph, triples, entityMentions, uniqueId);
                        HashMap<List<CoreLabel>, Entity> tokensToEntity = getTokensToEntity(entities);
                        HashMap<Entity, List<Entity>> entitySubsets = getEntitySubsets(entities);
                        
                        for (Map.Entry<Entity, List<Entity>> entitySubset : entitySubsets.entrySet()) {
                            entitySubset.getKey().setSubset(entitySubset.getValue());
                        }

                        List<String> allTriples = triples
                            .stream()
                            .map(t -> new Triple(tokensToEntity.get(t.subject), t.relationGloss(), tokensToEntity.get(t.object)))
                            .flatMap(t -> t.buildAllTriples().stream())
                            .filter(Triple::subjectAndObjectAreDifferent)
                            .filter(Triple::notEmpty)
                            .map(Triple::toString)
                            .distinct()
                            .toList();

                        tripleText += allTriples.stream().reduce("", (acc, t) -> acc + t + "\n");
                    }
                }
                writer.write(tripleText);

                reader.close();
                writer.close();
            } catch (FileNotFoundException e) {
                System.out.println("An error occurred.");
                e.printStackTrace();
            }
        }
    }

    public static List<Entity> getEntities(SemanticGraph baseGraph, Collection<RelationTriple> triples, List<CoreEntityMention> entityMentions, UUID uniqueId) {
        List<Entity> allEntities = new ArrayList<>();

        List<Entity> baseEntities = triples
            .stream()
            .flatMap(t ->
                Arrays.asList(
                    new Entity(t.subject, t.subjectGloss(), t.asDependencyTree().orElse(baseGraph), uniqueId), 
                    new Entity(t.object, t.objectGloss(), t.asDependencyTree().orElse(baseGraph), uniqueId)
                ).stream()
            )
            .distinct()
            .collect(toList());

        allEntities.addAll(baseEntities);

        entityMentions
            .stream()
            .filter(em -> !em.entityType().equals("NUMBER"))
            .map(em -> Entity.fromEntityMention(em, uniqueId))
            .forEach(me -> {
                baseEntities
                    .stream()
                    .filter(be -> be.getTokens().containsAll(me.getTokens()))
                    .forEach(be -> {
                        if (be.getTokens().equals(me.getTokens())) {
                            be.setNamedEntity(me.getMention());
                        } else if (!allEntities.contains(me)) {
                            me.setGraph(be.getGraph());
                            allEntities.add(me);
                        }
                    });
            });

        return allEntities;
    }

    public static HashMap<List<CoreLabel>, Entity> getTokensToEntity(List<Entity> entities) {
        HashMap<List<CoreLabel>, Entity> tokensToEntity = new HashMap<>();
        entities.forEach(e -> tokensToEntity.put(e.getTokens(), e));
        return tokensToEntity;
    }

    public static HashMap<Entity, List<Entity>> getEntitySubsets(List<Entity> entities) {
        HashMap<Entity, List<Entity>> entitySubset = new HashMap<>();
        
        for (Entity entity : entities) {
            List<Entity> subset = entities
                .stream()
                .filter(e -> entity.getTokens().containsAll(e.getTokens()) && !entity.equals(e))
                .collect(toList());
            entitySubset.put(entity, subset);
        }

        for (Entity entity : entities) {
            List<Entity> subset = entitySubset.get(entity);
            List<Entity> overlap = new ArrayList<>();
            for (Entity subsetEntity : subset) {
                List<Entity> secondDegreeSubset = entitySubset.get(subsetEntity);
                List<Entity> subsetEntityOverlap = subset.stream().filter(secondDegreeSubset::contains).collect(toList());
                overlap.addAll(subsetEntityOverlap);
            }
            entitySubset.put(entity, subset.stream().filter(e -> !overlap.contains(e)).collect(toList()));
        }

        return entitySubset;
    }
}
