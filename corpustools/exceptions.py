
class PCTError(Exception):
    pass

class DelimiterError(PCTError):
    pass

class ProdError(PCTError):
    def __init__(self, seg1, seg2, envs, missing, overlapping):
        self.segs = (seg1, seg2)
        self.envs = envs
        self.missing = missing
        self.overlapping = overlapping
        self.filename = 'pred_of_dist_{}_{}_error.txt'.format(seg1,seg2)
        self.information = ('Please refer to file \'{}\' in the errors directory '
                'for details or click on Show Details.').format(self.filename)
        if missing and overlapping:
            self.main = 'Exhaustivity and uniqueness were both not met for the segments {}.'.format(
                        ' and '.join([seg1, seg2]))

            self.value = ('Exhaustivity and uniqueness were both not met for the segments {}. '
                            '\n\nPlease refer to file {} in the errors directory '
                            'to view them.').format(
                        ' and '.join([seg1, seg2]),self.filename)
        elif missing:
            self.main = 'The environments specified were not exhaustive.'
            if len(missing.keys()) > 20:
                self.value = ('The environments specified were not exhaustive. '
                        'The segments {} were found in environments not specified. '
                        'The number of missing environments exceeded 20. '
                        '\n\nPlease refer to file {} in the errors directory '
                        'to view them.').format(
                        ' and '.join([seg1, seg2]),self.filename)
            else:
                self.value = ('The environments specified were not exhaustive. '
                    'The segments {} were found in environments not specified. '
                    'The following environments did not match any environments specified:\n\n{}'
                    '\n\nPlease refer to file {} in the errors directory '
                        'for details.').format(
                    ' and '.join([seg1, seg2]),
                    ' ,'.join(str(w) for w in missing.keys()),self.filename)

        elif overlapping:
            self.main = 'The environments specified were not unique.'
            if len(overlapping.keys()) > 10:
                self.value = ('The environments specified for the segments {} '
                            'were not unique. '
                            '\n\nPlease refer to file {} in the errors directory '
                            'to view them.').format(
                        ' and '.join([seg1, seg2]),self.filename)
            else:
                self.value = ('The environments specified were not unique. '
                            'The following environments for {} overlapped:\n\n'
                            ).format(' and '.join([seg1, seg2]))
                for k,v in overlapping.items():
                    self.value +='{}: {}\n'.format(
                            ' ,'.join(str(env) for env in k),
                            ' ,'.join(str(env) for env in v))
                self.value += ('\nPlease refer to file {} in the errors directory '
                        'for details.').format(self.filename)

        self.details = ''
        if self.missing:
            self.details += ('The following words have at least one of the '
                            'segments you are searching for, but it occurs in '
                            'an environment not included in the list you selected.\n\n')
            self.details += 'Segments you selected: {}, {}\n'.format(self.segs[0], self.segs[1])
            self.details += 'Environments you selected: {}\n\n'.format(' ,'.join(str(env) for env in self.envs))
            self.details += 'Word\tRelevant environments (segmental level only)\n'
            for wenv,words in self.missing.items():
                for w in words:
                    self.details += '{}\t{}\n'.format(w, wenv)
            if self.overlapping:
                self.details += '\n\n\n'
        if self.overlapping:
            self.details += ('The environments you selected are not unique, '
                    'which means that some of them pick out the same environment '
                    'in the same words.\n')
            self.details += ('For example, the environments of \'_[-voice]\' '
                    'and \'_k\', are not unique. They overlap with each '
                    'other, since /k/ is [-voice].\n')
            self.details += ('When your environments are not unique, the entropy '
                    'calculation will be inaccurate, since some environments '
                    'will be counted more than once.\n\n')
            self.details += 'Segments you selected: {}, {}\n'.format(self.segs[0], self.segs[1])
            self.details += 'Environments you selected: {}\n'.format(' ,'.join(str(env) for env in self.envs))
            self.details += 'Word\tWord environment\tOverlapping environments\n'
            for envs,v in self.overlapping.items():
                for wenv,w in v.items():
                    for word in w:
                        self.details += '{}\t{}\t{}\n'.format(
                                word,wenv,', '.join(envs))
    def __str__(self):
        return self.value

    def print_to_file(self,error_directory):
        with open(os.path.join(error_directory,self.filename),'w',encoding='utf-8') as f:
            if self.missing:
                print(('The following words have at least one of the '
                            'segments you are searching for, but it occurs in '
                            'an environment not included in the list you selected.'),file=f)
                print('Segments you selected: {}, {}'.format(self.segs[0], self.segs[1]),file=f)
                print('Environments you selected: {}'.format(' ,'.join(str(env) for env in self.envs)),file=f)
                print('Word\tRelevant environments (segmental level only)',file=f)
                for wenv,words in self.missing.items():
                    lines = list()
                    for w in words:
                        print('{}\t{}'.format(w, wenv),file=f)

            if self.overlapping:
                print(('The environments you selected are not unique, '
                    'which means that some of them pick out the same environment '
                    'in the same words.'),file=f)
                print(('For example, the environments of \'_[-voice]\' '
                    'and \'_k\', are not unique. They overlap with each '
                    'other, since /k/ is [-voice].'),file=f)
                print(('When your environments are not unique, the entropy '
                    'calculation will be inaccurate, since some environments '
                    'will be counted more than once.'),file=f)
                print(('This file contains all the words where this problem '
                    'could arise.'),file=f)
                print('',file=f)
                print('Segments you selected: {}, {}'.format(self.segs[0], self.segs[1]),file=f)
                print('Environments you selected: {}'.format(' ,'.join(str(env) for env in self.envs)),file=f)
                print('Word\tWord environment\tOverlapping environments',file=f)
                for envs,v in self.overlapping.items():
                    lines = list()
                    for wenv,w in v.items():
                        print('{}\t{}\t{}'.format(
                                w,wenv,', '.join(envs)),file=f)

class ILGError(PCTError):
    pass

class ILGWordMismatchError(PCTError):
    def __init__(self, spelling_line, transcription_line):
        self.main = "There doesn't appear to be equal numbers of words in the orthography and transcription lines."

        self.information = ''
        self.details = 'The following is the contents of the two lines:\n\n'
        self.details += '(line {}, {} words) '.format(spelling_line[0],len(spelling_line[1]))
        self.details += ' '.join(spelling_line[1]) + '\n'
        self.details += '(line {}, {} words) '.format(transcription_line[0],len(transcription_line[1]))
        self.details += ' '.join(transcription_line[1])

class ILGLinesMismatchError(PCTError):
    def __init__(self, lines):
        self.main = "There doesn't appear to be equal numbers of orthography and transcription lines"

        self.information = ''
        self.details = 'The following is the contents of the file after initial preprocessing:\n\n'
        for line in lines:
            self.details += line + '\n'
