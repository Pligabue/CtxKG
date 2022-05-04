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
        partialEntities.addAll(this.subsetRemovedEntities());
        partialEntities.removeIf(Entity::canBeDropped);
        return partialEntities;
    }

    private List<Entity> subsetRemovedEntities() {
        List<CoreLabel> subsetTokens = this.subset().stream().map(Entity::getTokens).flatMap(Collection::stream).collect(toList());

        List<Entity> remainingEntities = new ArrayList<>();
        List<CoreLabel> currentSequence = new ArrayList<>();
        String currentText = "";
        for (CoreLabel token : this.tokens()) {
            boolean subsetContainsToken = subsetTokens.contains(token);
            boolean isLastToken = (token == this.tokens().get(this.tokens().size() - 1));

            if (!subsetContainsToken) {
                currentSequence.add(token);
                currentText = currentText + " " + token.originalText();
            }
            
            if (!currentSequence.isEmpty() && (subsetContainsToken || isLastToken)) {
                remainingEntities.add(new Entity(currentSequence, currentText.trim(), this.graph(), this.groupId()));
                currentSequence = new ArrayList<>();
                currentText = "";
            }
        }
        return remainingEntities;
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
