import java.io.File;
import java.io.FileWriter;
import java.io.FilenameFilter;
import java.io.FileNotFoundException;
import java.util.Scanner;
import java.util.Collection;
import java.util.Properties;

import edu.stanford.nlp.ie.util.RelationTriple;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.naturalli.NaturalLogicAnnotations;
import edu.stanford.nlp.util.CoreMap;

public class TripleBuilder {

    public static void main(String[] args) throws Exception {
        // Create the Stanford CoreNLP pipeline
        Properties props = new Properties();
        // props.setProperty("openie.format", ""); // DOES NOT MAKE A DIFFERCE IN THIS APPLICATION.
        // props.setProperty("openie.filelist", ""); // DOES NOT MAKE A DIFFERCE IN THIS APPLICATION.
        // props.setProperty("openie.threads", ""); // DOES NOT MAKE A DIFFERCE IN THIS APPLICATION.
        // props.setProperty("openie.max_entailments_per_clause", "500"); // DOES NOT SEEM TO REALLY MAKE A DIFFERENCE.
        // props.setProperty("openie.resolve_coref", "true");
        props.setProperty("openie.ignore_affinity", "true"); // WHEN TRUE, REMOVES TRIPLES THAT HAVE AFFINITY BELOW 1.0. MIGHT BE USEFUL COMBINED WITH THE affinity_probability_cap PROPERTY.
        props.setProperty("openie.affinity_probability_cap", "1.0"); // SETTING IT TO 1.0 LEAVES ALL AFFINITY VALUES UNROUNDED. MIGHT BE USEFUL COMBINED WITH THE ignore_affinity PROPERTY.
        props.setProperty("openie.triple.strict", "false"); // WHEN FALSE, THE TRIPLES CHANGE SLIGHTLY. IT SEEMS MARGINALLY BETTER.
        // props.setProperty("openie.triple.all_nominals", "true"); // WHEN TRUE, THE NUMBER OF TRIPLES INCREASE A SMALL AMOUNT. THE EXTRA TRIPLES DO NOT SEEM VERY USEFUL THOUGH, THEY ARE MOSTLY INDICATING ADJECTIVES.
        // props.setProperty("openie.splitter.model", ""); // WILL NOT BE USED.
        props.setProperty("openie.splitter.nomodel", "true"); // DOES NOT CHANGE MUCH. SLIGHTLY BETTER AS TRUE.
        // props.setProperty("openie.splitter.disable", "true"); // THIS IS AN IMPORTANT ONE. WHEN TRUE, THE NUMBER OF TRIPLES IS MINIMAL.
        // props.setProperty("openie.affinity_models", ""); // WILL NOT BE USED.
        props.setProperty("annotators", "tokenize,ssplit,pos,lemma,depparse,natlog,openie");
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
                String tripleText = "";

                while (reader.hasNextLine()) {
                    String line = reader.nextLine();
                    Annotation doc = new Annotation(line);
                    pipeline.annotate(doc);
                    
                    for (CoreMap sentence : doc.get(CoreAnnotations.SentencesAnnotation.class)) {
                        Collection<RelationTriple> triples = sentence.get(NaturalLogicAnnotations.RelationTriplesAnnotation.class);
                        for (RelationTriple triple : triples) {
                            tripleText += triple.confidence + ";" +
                                          triple.subjectLemmaGloss() + ";" +
                                          triple.relationLemmaGloss() + ";" +
                                          triple.objectLemmaGloss() + "\n";
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
