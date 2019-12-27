import os
import copy
import json
import nltk
import argparse


class Station(object):
    def __init__(self):
        self.inp = None  # as a char
        self.out = None # as a list of char
        self.idx = None

    def __repr__(self):
        return '{} -> {}, {}'.format(self.inp, self.out, self.idx)

    def __hash__(self):
        return hash((self.inp, tuple(self.out), self.idx))

    def __eq__(self, other):
        if isinstance(other, Station):
            return self.inp == other.inp and self.out == other.out and self.idx == other.idx
        return NotImplemented


class Table(object):
    def __init__(self, idx):
        self.idx = idx
        self.stations = list()

    def __repr__(self):
        repr_str = "="*40 + '\n'
        for station in self.stations:
            repr_str += station.__repr__()
            repr_str += '\n'

        repr_str += "="*40 + '\n'
        return repr_str


class Grammar(Table):
    def __init__(self, grammar):
        super().__init__('Grammar')
        for key in grammar.keys():
            for infer in grammar[key]:
                st = Station()
                st.inp = key

                st.out = infer
                st.idx = -1

                self.stations.append(st)


class EarleyParser:
    def __init__(self, sentences, grammar):
        self.sentences = sentences
        self.tokens, self.word_type_dict = self.tokenize(sentences)
        self.grammar = grammar
        self.tables = list()

    # ---------------- Utilities -----------------
    @staticmethod
    def tokenize(sentences):
        print('Tokenizing ....')
        nltk.download('brown', quiet=True)
        nltk.download('universal_tagset', quiet=True)

        word_dictionary = nltk.corpus.brown.tagged_words(tagset='universal')

        #
        word_type_dict = {}
        tokens = list(sentences.split(' '))

        for token in tokens:
            token = token.lower()
            word_type_dict[token] = set()
            for word in word_dictionary:
                if word[0].lower() == token.lower():
                    tag = word[1].lower()
                    if tag == 'adp':
                        tag = 'prep'

                    if tag == 'pron':
                        tag = 'noun'

                    word_type_dict[token].add(tag)

            word_type_dict[token] = list(word_type_dict[token])

        print(tokens)
        print(word_type_dict)
        print()
        return tokens, word_type_dict

    @staticmethod
    def _move_dot(station):
        result_state = copy.deepcopy(station)

        dot_idx = -1
        for idx, element in enumerate(result_state.out):
            if element == '.':
                dot_idx = idx
                del result_state.out[idx]
                break

        result_state.out.insert(dot_idx+1, '.')
        return result_state

    @staticmethod
    def is_expand(station_out):
        dot_positions = [i for i, x in enumerate(station_out) if x == '.']
        if len(dot_positions) > 0:
            dot_pos = dot_positions[0]
        else:
            return False, None

        if dot_pos == len(station_out) - 1:
            return False, None

        return station_out[dot_pos+1].isupper(), station_out[dot_pos+1]

    @staticmethod
    def is_input(station_out, terminal):
        dot_positions = [i for i, x in enumerate(station_out) if x == '.']
        if len(dot_positions) > 0:
            dot_pos = dot_positions[0]
        else:
            return False

        if dot_pos == len(station_out) - 1:
            return False

        return station_out[dot_pos+1].islower() and station_out[dot_pos + 1] == terminal

    @staticmethod
    def is_backtrack(station_out):
        return station_out[-1] == '.'


    @staticmethod
    def is_overlap(station, table):
        table_clone = copy.deepcopy(table)
        table_clone_1 = copy.deepcopy(table)

        table_clone_1.stations.append(station)

        return set(table_clone_1.stations) == set(table_clone.stations)

    # ----------- Main Methods -----------------
    def _get_table_by_idx(self, idx):
        for table in self.tables:
            if table.idx == idx:
                return table

        return None

    def _expand(self, src_table, dst_table, non_terminal):
        for station in src_table.stations:
            if station.inp == non_terminal:
                dst_station = self._move_dot(station)
                dst_station.idx = dst_table.idx
                if not self.is_overlap(dst_station, dst_table):
                    dst_table.stations.append(dst_station)

    def _input(self, station, dst_table):
        dst_station = self._move_dot(station)
        dst_station.idx = station.idx
        if not self.is_overlap(dst_station, dst_table):
            dst_table.stations.append(dst_station)

    def _backtrack(self, src_table, dst_table, non_terminal):
        for station in src_table.stations:
            for i, element in enumerate(station.out):
                if element == non_terminal and i > 0 and station.out[i-1] == '.':
                    dst_station = self._move_dot(station)
                    if not self.is_overlap(dst_station, dst_table):
                        dst_table.stations.append(dst_station)

                    break


    def parse(self):
        self._step_1()
        table_0_clone = copy.deepcopy(self.tables[0])
        while True:
            self._step_2()
            self._step_3()
            if table_0_clone.stations == self.tables[0].stations:
                break

            table_0_clone = copy.deepcopy(self.tables[0])

        print('Table 0: ')
        print(self.tables[0])

        for idx, token in enumerate(self.tokens):
            self._step_4(token, idx+1)
            cur_table_clone = copy.deepcopy(self.tables[idx+1])
            while True:
                self._step_5(idx+1)
                self._step_6(idx+1)
                if cur_table_clone.stations == self.tables[idx+1].stations:
                    break

                cur_table_clone = copy.deepcopy(self.tables[idx+1])

            print('Table {}: {} / {}'.format(idx+1, token, self.word_type_dict[token]))
            print(self.tables[idx+1])

        is_right_sent = False
        for station in self.tables[len(self.tokens)].stations:
            if self.is_backtrack(station.out) and station.inp == 'S':
                is_right_sent = True

        print('Right sentence' if is_right_sent else 'Wrong sentence')

    def _step_1(self):
        table_0 = Table(0)
        self._expand(self.grammar, table_0, 'S')
        self.tables.append(table_0)

    def _step_2(self):
        table_0 = self._get_table_by_idx(0)
        table_0_for_checking = copy.deepcopy(table_0)
        for station in table_0.stations:
            if self.is_backtrack(station.out):
                self._backtrack(table_0, table_0, station.inp)


    def _step_3(self):
        table_0 = self._get_table_by_idx(0)
        table_0_for_checking = copy.deepcopy(table_0)
        for station in table_0.stations:
            if self.is_expand(station.out)[0]:
                B = self.is_expand(station.out)[1]
                self._expand(self.grammar, table_0, B)


    def _step_4(self, token, idx):
        terminals = self.word_type_dict[token]
        prev_table = self._get_table_by_idx(idx - 1)
        cur_table = Table(idx)

        for station in prev_table.stations:
            for terminal in terminals:
                if self.is_input(station.out, terminal):
                    self._input(station, cur_table)

        self.tables.append(cur_table)


    def _step_5(self, idx):
        cur_table = self._get_table_by_idx(idx)
        table_for_checking = copy.deepcopy(cur_table)

        for station in cur_table.stations:
            if self.is_backtrack(station.out):
                backtrack_table = self._get_table_by_idx(station.idx)
                self._backtrack(backtrack_table, cur_table, station.inp)


    def _step_6(self, idx):
        cur_table = self._get_table_by_idx(idx)
        table_for_checking = copy.deepcopy(cur_table)

        for station in cur_table.stations:
            if self.is_expand(station.out)[0]:
                B = self.is_expand(station.out)[1]
                self._expand(self.grammar, cur_table, B)


    def _build_tree(self):
        pass


def main():
    with open('./grammar/grammar1.txt','r') as fb:
        grammar = json.load(fb)

    grammar = Grammar(grammar)

    parser = argparse.ArgumentParser()
    parser.add_argument('--sentence', type=str, default='a young man in the dirty class')

    sentence = parser.parse_args().sentence

    ep = EarleyParser(sentence, grammar)
    ep.parse()

if __name__ == '__main__':
    main()

