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

        File folder = new File("./documents/");
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
                String tripleText = "confidence;subject;relation;object;subject_id;object_id\n";
                String prefix = UUID.randomUUID().toString();

                while (reader.hasNextLine()) {
                    String line = reader.nextLine();
                    CoreDocument doc = new CoreDocument(line);
                    pipeline.annotate(doc);
                    List<CoreEntityMention> entityMentions= doc.entityMentions()
                        .stream()
                        .sorted((em1, em2)-> Integer.compare(em2.tokens().size(), em1.tokens().size()))
                        .collect(toList());

                    for (CoreMap sentence : doc.annotation().get(CoreAnnotations.SentencesAnnotation.class)) {
                        Collection<RelationTriple> triples = sentence.get(NaturalLogicAnnotations.RelationTriplesAnnotation.class);
                        for (RelationTriple triple : triples) {
                            String confidence = Double.toString(triple.confidence), subject = triple.subjectGloss(), relation = triple.relationGloss(), object = triple.objectGloss();
                            final String initialSubject = triple.subjectGloss(), initialObject = triple.objectGloss();
                            String tripleToAdd = null;
                            List<CoreLabel> subjectTokens = triple.canonicalSubject;
                            List<CoreLabel> objectTokens = triple.canonicalObject;
                            CoreEntityMention subjectNamedEntityMention = null;
                            CoreEntityMention objectNamedEntityMention = null;
                            Optional<CoreEntityMention> subjectNamedEntityMentionOptional = entityMentions.stream().filter(em -> initialSubject.contains(em.text())).findFirst();   
                            Optional<CoreEntityMention> objectNamedEntityMentionOptional = entityMentions.stream().filter(em -> initialObject.contains(em.text())).findFirst();        

                            if (subjectNamedEntityMentionOptional.isPresent()) {
                                subjectNamedEntityMention = subjectNamedEntityMentionOptional.get();
                                if (subject.equals(subjectNamedEntityMention.text())) {
                                    subject = subjectNamedEntityMention.text();
                                    subjectTokens = subjectNamedEntityMention.tokens();
                                } else {
                                    tripleToAdd = buildTripleRow("1.0", subject, "relates to", subjectNamedEntityMention.text(), buildID(prefix, subjectTokens), buildID(prefix, subjectNamedEntityMention.tokens()));
                                    if (isNewTriple(tripleText, tripleToAdd))
                                        tripleText += tripleToAdd;
                                }
                            }
                            if (objectNamedEntityMentionOptional.isPresent()) {
                                objectNamedEntityMention = objectNamedEntityMentionOptional.get();
                                if (object.equals(objectNamedEntityMention.text())) {
                                    object = objectNamedEntityMention.text();
                                    objectTokens = objectNamedEntityMention.tokens();
                                } else {
                                    tripleToAdd = buildTripleRow("1.0", object, "relates to", objectNamedEntityMention.text(), buildID(prefix, objectTokens), buildID(prefix, objectNamedEntityMention.tokens()));
                                    if (isNewTriple(tripleText, tripleToAdd))
                                        tripleText += tripleToAdd;
                                }
                            }
                            tripleText += buildTripleRow(confidence, subject, relation, object, buildID(prefix, subjectTokens), buildID(prefix, objectTokens));
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

    public static String buildID(String prefix, List<CoreLabel> tokens) {
        return prefix + tokens.stream().reduce("", (acc, token) -> acc + "-" + token.toString(), String::concat);
    }

    public static String buildTripleRow(String confidence, String subject, String relation, String object, String subjectID, String objectID) {
        return confidence + ";" + subject + ";" + relation + ";" + object + ";" + subjectID + ";" + objectID + "\n";
    }

    public static boolean isNewTriple(String tripleText, String tripleToAdd) {
        return !tripleText.contains(tripleToAdd);
    }
}
