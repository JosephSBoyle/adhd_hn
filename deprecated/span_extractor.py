import re
import collections

SpanTuple = collections.namedtuple("SpanIndexTuple", "start,end")

def get_span_indices_from_tagged_text(tagged_text: str) -> dict[str, list[SpanTuple]]:
    """Create a map from tags to a list of two-tuples containing their start and stop
    positions in the tagged piece of text."""

    tag_indices = collections.defaultdict(list)

    # Track the cumulative number of characters used in tags up to the current point.
    # Subtract this amount to map indices in tagged text to indices in un-tagged text.
    cumulutive_tag_chars = 0
    for match in re.finditer(r'<(\d+)>(.*?)<\/\d+>', tagged_text):
        tag_type = match.group(1)
        tag_chars = len(tag_type)

        # Start of span idx.
        cumulutive_tag_chars += (tag_chars + 2) # tag length + len("<>")
        start_idx = match.start(2) - cumulutive_tag_chars

        # End of span idx.
        end_idx = match.end(2) - cumulutive_tag_chars
        cumulutive_tag_chars += (tag_chars + 3) # tag length + len("<\>")

        tag_indices[tag_type].append(SpanTuple(start_idx, end_idx))

    return tag_indices


if __name__ == "__main__":
    #### Test ####
    tagged_text = "<2>Female</2> patient, 35 years old, presents with complaints of <1>decrease in energy</1>, <1>tiredness</1>, and <777>loss of energy</777>."
    untagged_text = "Female patient, 35 years old, presents with complaints of decrease in energy, tiredness, and loss of energy."
    result = get_span_indices_from_tagged_text(tagged_text)

    spans = []
    for k in result.keys():
        for span in result[k]:
            spans.append(untagged_text[span.start: span.end])

    assert spans == ["Female", "decrease in energy", "tiredness", "loss of energy"]
