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


public class TripleBuilder {

    public static void main(String[] args) throws Exception {
        // Create the Stanford CoreNLP pipeline
        Properties props = new Properties();
        // props.setProperty("openie.format", ""); // DOES NOT MAKE A DIFFERCE IN THIS APPLICATION.
        // props.setProperty("openie.filelist", ""); // DOES NOT MAKE A DIFFERCE IN THIS APPLICATION.
        // props.setProperty("openie.threads", ""); // DOES NOT MAKE A DIFFERCE IN THIS APPLICATION.
        // props.setProperty("openie.max_entailments_per_clause", "500"); // DOES NOT SEEM TO REALLY MAKE A DIFFERENCE.
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

        File folder = new File("./sentences/");
        FilenameFilter filter = new FilenameFilter() {
            @Override
            public boolean accept(File f, String name) {
                boolean isTXT = name.endsWith(".txt");
                boolean tripleExists = (new File("./triples/" + name)).exists();
                
                return isTXT && !tripleExists;
            }
        };
        File[] files = folder.listFiles(filter);

        for (File f : files) {
            try {
                Scanner reader = new Scanner(f, "utf-8");
                FileWriter writer = new FileWriter("./triples/" + f.getName());
                String tripleText = "confidence;subject;relation;object;subject_named_entity;object_named_entity\n";

                while (reader.hasNextLine()) {
                    String line = reader.nextLine();
                    CoreDocument doc = new CoreDocument(line);
                    pipeline.annotate(doc);
                    List<CoreEntityMention> entityMentions= doc.entityMentions();
                    List<List<CoreLabel>> entityTokens = entityMentions.stream().map(em -> em.tokens()).collect(toList());

                    for (CoreMap sentence : doc.annotation().get(CoreAnnotations.SentencesAnnotation.class)) {
                        Collection<RelationTriple> triples = sentence.get(NaturalLogicAnnotations.RelationTriplesAnnotation.class);
                        for (RelationTriple triple : triples) {
                            List<CoreLabel> subjectTokens = triple.canonicalSubject;
                            List<CoreLabel> objectTokens = triple.canonicalObject;
                            String subjectNamedEntity = "";
                            String objectNamedEntity = "";
                            Optional<CoreEntityMention> subjectNamedEntityMatch = entityMentions.stream().filter(em -> subjectTokens.containsAll(em.tokens())).findAny();   
                            Optional<CoreEntityMention> objectNamedEntityMatch = entityMentions.stream().filter(em -> objectTokens.containsAll(em.tokens())).findAny();

                            if (subjectNamedEntityMatch.isPresent())
                                subjectNamedEntity = subjectNamedEntityMatch.get().text();
                            if (objectNamedEntityMatch.isPresent())
                                objectNamedEntity = objectNamedEntityMatch.get().text();

                            tripleText += triple.confidence + ";" +
                                          triple.subjectGloss() + ";" +
                                          triple.relationGloss() + ";" +
                                          triple.objectGloss() + ";" +
                                          subjectNamedEntity + ";" + 
                                          objectNamedEntity + "\n";
                        }
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
}
