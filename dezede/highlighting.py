from haystack.utils import Highlighter


class CustomHighlighter(Highlighter):
    def find_window(self, highlight_locations):
        max_length = self.max_length
        default_margin = max_length // 2
        best_start = 0
        best_end = max_length

        # First, make sure we have words.
        if not highlight_locations:
            return best_start, best_end

        words_found = []

        # Next, make sure we found any words at all.
        for word, offset_list in highlight_locations.items():
            if offset_list:
                # Add all of the locations to the list.
                words_found.extend(offset_list)

        if not words_found:
            return best_start, best_end

        def get_ends(start, margin=default_margin):
            """Returns the end points so that a margin is added."""
            # TODO: Take the word lengths into account.
            best_start = max(0, start - margin)
            best_end = best_start + max_length
            return best_start, best_end

        # Sort the list so it's in ascending order.
        words_found = sorted(words_found)

        best_start, best_end = get_ends(words_found[0])

        if len(words_found) == 1:
            return best_start, best_end

        # We now have a denormalized list of all positions were a word was
        # found. We'll iterate through and find the densest window we can by
        # counting the number of found offsets (-1 to fit in the window).
        highest_density = 0

        for i, start in enumerate(words_found[:-1]):
            current_density = 1

            for end in words_found[i + 1:]:
                if end - start >= max_length:
                    break
                current_density += 1

                # Only replace if we have a bigger (not equal density) so we
                # give deference to windows earlier in the document.
                if current_density > highest_density:
                    margin = (max_length - (end - start)) // 2
                    best_start, best_end = get_ends(start, margin)
                    highest_density = current_density

        return best_start, best_end
