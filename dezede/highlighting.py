# coding: utf-8

from __future__ import unicode_literals
from haystack.utils import Highlighter


class CustomHighlighter(Highlighter):
    def find_window(self, highlight_locations):
        best_start = 0
        best_end = self.max_length

        # First, make sure we have words.
        if not len(highlight_locations):
            return best_start, best_end

        words_found = []

        # Next, make sure we found any words at all.
        for word, offset_list in highlight_locations.items():
            if len(offset_list):
                # Add all of the locations to the list.
                words_found.extend(offset_list)

        if not len(words_found):
            return best_start, best_end

        if len(words_found) == 1:
            best_start = max(0, words_found[0] - self.max_length / 2)
            return best_start, best_start + self.max_length

        # Sort the list so it's in ascending order.
        words_found = sorted(words_found)

        # We now have a denormalized list of all positions were a word was
        # found. We'll iterate through and find the densest window we can by
        # counting the number of found offsets (-1 to fit in the window).
        highest_density = 0

        if words_found[:-1][0] > self.max_length:
            best_start = words_found[:-1][0]
            best_end = best_start + self.max_length

        for count, start in enumerate(words_found[:-1]):
            current_density = 1

            for end in words_found[count + 1:]:
                if end - start < self.max_length:
                    current_density += 1
                else:
                    current_density = 0

                # Only replace if we have a bigger (not equal density) so we
                # give deference to windows earlier in the document.
                if current_density > highest_density:
                    best_start = start
                    best_end = start + self.max_length
                    highest_density = current_density

        return best_start, best_end
