package com.triplebuilder.app;


import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.Collection;
import java.util.Collections;
import java.util.Objects;

import static java.util.stream.Collectors.*;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.CoreEntityMention;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.ling.IndexedWord;


public class Entity {
    private static List<String> expectedNounTags = Arrays.asList("NN", "NNP", "NNS", "NNPS");
    private static List<String> trimmableTags = Arrays.asList("IN");
    private static List<String> droppableTags = Arrays.asList("POS");
    private List<CoreLabel> tokens;
    private String text;
    private CoreEntityMention mention;
    private SemanticGraph graph;
    private UUID groupId;
    private Integer treeLevel;
    private List<Entity> subset;
    private List<String> tags;
    private EntitySplitter splitter;

    public Entity(List<CoreLabel> tokens, String text, SemanticGraph graph, UUID groupId) {
        this.tokens = tokens;
        this.text = text;
        this.mention = null;
        this.graph = graph;
        this.groupId = groupId;
        this.subset = Collections.emptyList();
        this.tags = null;
        this.splitter = new EntitySplitter(this);
    }

    public static Entity fromEntityMention(CoreEntityMention mention, UUID groupId) {
        return new Entity(mention.tokens(), mention.text(), null, groupId).setNamedEntity(mention);
    }

    public Entity cleanForm() {
        List<CoreLabel> cleanTokens = this.tokens.stream().filter(t -> !droppableTags.contains(t.tag())).collect(toList());
        trimTokens(cleanTokens);
        String cleanText = cleanTokens.stream().reduce("", (acc, token) -> acc + " " + token.originalText(), String::concat).strip();
        return new Entity(cleanTokens, cleanText, this.graph, this.groupId).setNamedEntity(this.mention);
    }

    public String getId() {
        return this.mention != null
            ? ("NE-" + this.mention.entityType() + "-" + this.mention.text()).replaceAll("\s+", "-")
            : (this.groupId + this.tokens.stream().reduce("", (acc, token) -> acc + "-" + token.toString(), String::concat)).replaceAll("\s+", "-");
    }

    public Entity getFinalEntity() {
        if (this.subset.isEmpty()) {
            return this;
        }
        return this.splitter.getMainPartialEntity().getFinalEntity();
    }

    public List<Triple> buildDerivativeTriples() {
        return this.splitter.buildDerivativeTriples();
    }

    public int compareTo(Entity e) {
        int levelComparison = -Integer.compare(this.getTreeLevel(), e.getTreeLevel());
        int sizeComparison = Integer.compare(this.getTokens().size(), e.getTokens().size());

        if (levelComparison == 0) {
            return sizeComparison;
        }
        return levelComparison;
    }

    @Override
    public String toString() {
        return this.mention != null
            ? "<Entity NER text=\"" + this.text + "\" tokens=" + this.tokens + ">"
            : "<Entity text=\"" + this.text + "\" tokens=" + this.tokens + ">";
    };

    @Override
    public boolean equals(Object obj) {
        if (obj == this)
            return true;

        if (obj.getClass() != this.getClass())
            return false;

        Entity entityObj = (Entity) obj;

        return this.getId().equals(entityObj.getId());
    };

    @Override
    public int hashCode() {
        return this.getTokens().hashCode();
    };

    public String getText() {
        return this.text;
    }

    public List<CoreLabel> getTokens() {
        return this.tokens;
    }

    public List<String> getTags() {
        if (this.tags == null) {
            this.tags = this.tokens.stream().map(CoreLabel::tag).collect(toList());
        }
        return this.tags;
    }

    public UUID getGroupId() {
        return this.groupId;
    }

    public CoreEntityMention getMention() {
        return this.mention;
    }

    public SemanticGraph getGraph() {
        return this.graph;
    }

    public Integer getTreeLevel() {
        if (this.treeLevel == null) {
            this.treeLevel = calculateTreeLevel(this.graph.getRoots(), 0);
        }
        return this.treeLevel;
    }

    private Integer calculateTreeLevel(Collection<IndexedWord> nodes, Integer level) {
        List<CoreLabel> tokens = nodes.stream().map(node -> node.backingLabel()).collect(toList());
        boolean anyTokenInEntity = this.tokens.stream().anyMatch(tokens::contains);

        if (anyTokenInEntity) {
            return level;
        }

        return nodes
            .stream()
            .map(node -> calculateTreeLevel(this.graph.getChildren(node), level + 1))
            .filter(Objects::nonNull)
            .min(Integer::compareTo)
            .orElse(null);
    }

    public List<Entity> getSubset() {
        return this.subset;
    }
    
    public Entity setNamedEntity(CoreEntityMention mention) {
        this.mention = mention;
        return this;
    }

    public Entity setSubset(List<Entity> subset) {
        this.subset = subset;
        return this;
    }

    public Entity setGraph(SemanticGraph graph) {
        this.graph = graph;
        return this;
    }

    public boolean hasNoun() {
        return this.getTags().stream().anyMatch(tag -> expectedNounTags.contains(tag));
    }

    public boolean canBeDropped() {
        return droppableTags.containsAll(this.getTags());
    }

    private static void trimTokens(List<CoreLabel> tokens) {
        boolean changed;
        do {
            changed = false;
            if (tokens.size() > 0) {
                CoreLabel firstToken = tokens.get(0);
                CoreLabel lastToken = tokens.get(tokens.size() - 1);
                
                if (trimmableTags.contains(firstToken.tag())) {
                    changed |= tokens.remove(firstToken);
                }
                if (trimmableTags.contains(lastToken.tag())) {
                    changed |= tokens.remove(lastToken);
                }
            }
        } while (changed);
    }
}
