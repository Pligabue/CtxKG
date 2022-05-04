package openie;

import java.lang.Comparable;
import java.text.NumberFormat.Style;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Objects;

import static java.util.stream.Collectors.*;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.CoreEntityMention;
import edu.stanford.nlp.semgraph.SemanticGraph;
import edu.stanford.nlp.ling.IndexedWord;


public class EntitySplitter {
    private Entity entity;

    public EntitySplitter(Entity entity) {
        this.entity = entity;
    }

    public List<Triple> buildDerivativeTriples() {
        if (this.subset().isEmpty()) {
            return Collections.emptyList();
        }

        Entity mainPartialEntity = this.getMainPartialEntity();
        return this.getPartialEntities()
            .stream()
            .filter(e -> !mainPartialEntity.getFinalEntity().equals(e.getFinalEntity()))
            .map(e -> Triple.buildTriple(this.entity, e, this.graph()))
            .filter(Objects::nonNull)
            .collect(toList());
    }

    public Entity getMainPartialEntity() {
        return this.getPartialEntities().stream().max(Entity::compareTo).get();
    }

    private List<Entity> getPartialEntities() {
        List<Entity> partialEntities = new ArrayList<>(this.subset());
        partialEntities.add(this.subsetRemovedEntity());
        partialEntities = partialEntities.stream().filter(e -> !e.canBeDroped()).collect(toList());
        return partialEntities;
    }

    private Entity subsetRemovedEntity() {
        List<CoreLabel> subsetTokens = this.subset().stream().map(Entity::getTokens).flatMap(Collection::stream).collect(toList());
        List<CoreLabel> remainingTokens = this.tokens().stream().filter(t -> !subsetTokens.contains(t)).collect(toList());
        String remainingText = remainingTokens.stream().reduce("", (acc, token) -> acc + " " + token.originalText(), String::concat).strip();
        return new Entity(remainingTokens, remainingText, this.graph(), this.groupId());
    }

    private List<Entity> subset() {
        return this.entity.getSubset();
    }

    private List<CoreLabel> tokens() {
        return this.entity.getTokens();
    }

    private UUID groupId() {
        return this.entity.getGroupId();
    }

    private SemanticGraph graph() {
        return this.entity.getGraph();
    }
}
