import edu.stanford.nlp.ie.util.RelationTriple;
import edu.stanford.nlp.simple.*;
import java.io.File;
import java.io.FileWriter;
import java.io.FilenameFilter;
import java.io.FileNotFoundException;
import java.util.Scanner;

/** A demo illustrating how to call the OpenIE system programmatically.
 */
public class TripleBuilder {

    public static void main(String[] args) throws Exception {

        File folder = new File("./sentences/");
        FilenameFilter filter = new FilenameFilter() {
            @Override
            public boolean accept(File f, String name) {
                return name.endsWith(".txt");
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
                    Document doc = new Document(line);
                    // Iterate over the sentences in the document
                    for (Sentence sent : doc.sentences()) {
                        // Iterate over the triples in the sentence
                        for (RelationTriple triple : sent.openieTriples()) {
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
