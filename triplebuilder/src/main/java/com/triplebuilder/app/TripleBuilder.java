package com.triplebuilder.app;


import com.triplebuilder.app.*;

import java.io.File;
import java.io.FileWriter;
import java.io.FilenameFilter;
import java.io.FileNotFoundException;
import java.util.Scanner;
import java.util.Collection;
import java.util.Properties;
import java.util.List;
import java.util.ArrayList;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Function;
import java.util.HashMap;
import java.util.Map;
import java.util.Arrays;
import static java.util.stream.Collectors.*;

import edu.stanford.nlp.ie.util.RelationTriple;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.pipeline.CoreDocument;
import edu.stanford.nlp.pipeline.CoreEntityMention;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.naturalli.NaturalLogicAnnotations;
import edu.stanford.nlp.util.CoreMap;
import edu.stanford.nlp.ling.CoreLabel;

import edu.stanford.nlp.semgraph.SemanticGraphCoreAnnotations.BasicDependenciesAnnotation;
import edu.stanford.nlp.semgraph.SemanticGraph;

import org.apache.commons.io.FileUtils;
// import org.apache.commons.io.IOFileFilter;

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

        File documentFolder = new File("./documents/");
        File tripleFolder = new File("./triples/");

        Collection<File> files = FileUtils.listFiles(documentFolder, new String[] {"txt"}, true);
        int numberOfFiles = files.size();
        int fileIndex = 0;
        for (File f : files) {
            printProgress(fileIndex, numberOfFiles);
            fileIndex++;

            String targetFilename = f.getPath().replace(documentFolder.getPath(), tripleFolder.getPath()).replace(".txt", ".csv");
            File targetFile = new File(targetFilename);
            if (targetFile.exists()) {
                continue;
            }

            try {
                Scanner reader = new Scanner(f, "utf-8");
                FileWriter writer = null;
                UUID uniqueId = UUID.randomUUID();
                List<String> allTriples = new ArrayList<>();
                allTriples.add(Triple.getHeader(f.getAbsolutePath()));
                
                while (reader.hasNextLine()) {
                    String line = reader.nextLine();
                    CoreDocument doc = new CoreDocument(line);
                    pipeline.annotate(doc);
                    List<CoreEntityMention> entityMentions = doc.entityMentions();

                    for (CoreMap sentence : doc.annotation().get(CoreAnnotations.SentencesAnnotation.class)) {
                        SemanticGraph graph = sentence.get(BasicDependenciesAnnotation.class);
                        Collection<RelationTriple> triples = sentence.get(NaturalLogicAnnotations.RelationTriplesAnnotation.class);
                        List<Entity> entities = getEntities(graph, triples, entityMentions, uniqueId);
                        Map<List<CoreLabel>, Entity> tokensToEntity = entities.stream().collect(toMap(Entity::getTokens, Function.identity()));
                        Map<Entity, List<Entity>> entitySubsets = getEntitySubsets(entities);
                        
                        for (Map.Entry<Entity, List<Entity>> entitySubset : entitySubsets.entrySet()) {
                            entitySubset.getKey().setSubset(entitySubset.getValue());
                        }

                        allTriples.addAll(
                            triples
                                .stream()
                                .map(t -> new Triple(tokensToEntity.get(t.subject), t.relationGloss(), tokensToEntity.get(t.object)))
                                .flatMap(t -> t.buildAllTriples().stream())
                                .filter(Triple::subjectAndObjectAreDifferent)
                                .filter(Triple::notEmpty)
                                .map(Triple::toString)
                                .toList()
                        );
                    }
                }
                writer = new FileWriter(targetFilename);
                writer.write(allTriples.stream().distinct().collect(joining("\n")));
                writer.close();
                reader.close();
            } catch (FileNotFoundException e) {
                System.out.println("An error occurred.");
                e.printStackTrace();
            }
        }
        printProgress(fileIndex, numberOfFiles);
        System.out.println();
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
                Optional<Entity> exactMatch = baseEntities.stream().filter(be -> be.getTokens().equals(me.getTokens())).findAny();
                Optional<Entity> containsMatch = baseEntities.stream().filter(be -> be.getTokens().containsAll(me.getTokens())).findAny();

                if (exactMatch.isPresent()) {
                    exactMatch.get().setNamedEntity(me.getMention());
                } else if (containsMatch.isPresent()) {
                    me.setGraph(containsMatch.get().getGraph());
                    allEntities.add(me);
                }
            });

        return allEntities;
    }

    public static HashMap<Entity, List<Entity>> getEntitySubsets(List<Entity> entities) {
        HashMap<Entity, List<Entity>> entitySubset = new HashMap<>();
        
        for (Entity entity : entities) {
            List<Entity> subset = entities
                .stream()
                .filter(e -> entity.getTokens().containsAll(e.getTokens()) && entity.getTokens().size() > e.getTokens().size())
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

    public static String getRelativePath(File baseDir, File file) {
        int rootLength = baseDir.getAbsolutePath().length();
        String absFileName = file.getAbsolutePath();
        String relFileName = absFileName.substring(rootLength + 1);
        return relFileName;
    }

    public static void printProgress(int current, int size) {
        int totalSections = 50;
        int filledSections = size > 0 ? (totalSections * current) / size : totalSections;
        int emptySections = totalSections - filledSections;
        int percentage = size > 0 ? (100 * current) / size : 100;
        System.out.print("\r[" + "#".repeat(filledSections) + " ".repeat(emptySections) + "] " + current + "/" + size + " " + percentage + "%");
    }
}
