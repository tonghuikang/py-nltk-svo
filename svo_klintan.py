# -*- coding: utf-8 -*-
import os
import nltk
from nltk.tree import *
from nltk.parse import stanford
import nltk.data
import nltk.draw
import os
import sys

# reload(sys)
# sys.setdefaultencoding("utf-8")

# os.environ['CLASSPATH'] = '/Users/hkmac/Desktop/stanford-corenlp-full-2018-02-27/'
# os.environ['STANFORD_MODELS'] = '/Users/hkmac/Desktop/questionable-statements/py-nltk-svo/stanford-openie/stanford-openie-models.jar'

class SVO(object):
    """
    Class Methods to Extract Subject Verb Object Tuples from a Sentence
    """
    def __init__(self):
        """
        Initialize the SVO Methods
        """
        self.noun_types = ["NN", "NNP", "NNPS","NNS","PRP"]
        self.verb_types = ["VB","VBD","VBG","VBN", "VBP", "VBZ"]
        self.adjective_types = ["JJ","JJR","JJS"]
        self.pred_verb_phrase_siblings = None
        
        stanford_parser_jar = '/Users/hkmac/Desktop/stanford-parser-full-2018-02-27/stanford-parser.jar'
        stanford_model_jar = '/Users/hkmac/Desktop/stanford-parser-full-2018-02-27/stanford-parser-3.9.1-models.jar'
        
        self.parser = stanford.StanfordParser(path_to_jar=stanford_parser_jar, path_to_models_jar=stanford_model_jar)
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    def get_attributes(self,node,parent_node, parent_node_siblings):
        """
        returns the Attributes for a Node
        """

    def get_subject(self,sub_tree):
        """
        Returns the Subject and all attributes for a subject, sub_tree is a Noun Phrase
        """
        sub_nodes = []
        sub_nodes = sub_tree.subtrees()
        sub_nodes = [each for each in sub_nodes if each.pos()]
        subject = None

        for each in sub_nodes:

            if each.label() in self.noun_types:
                subject = each.leaves()
                break

        return {'subject':subject}

    def get_object(self,sub_tree):
        """
        Returns an Object with all attributes of an object
        """
        siblings = self.pred_verb_phrase_siblings
        Object = None
        for each_tree in sub_tree:
            if each_tree.label() in ["NP","PP"]:
                sub_nodes = each_tree.subtrees()
                sub_nodes = [each for each in sub_nodes if each.pos()]

                for each in sub_nodes:
                    if each.label() in self.noun_types:
                        Object = each.leaves()
                        break
                break
            else:
                sub_nodes = each_tree.subtrees()
                sub_nodes = [each for each in sub_nodes if each.pos()]
                for each in sub_nodes:
                    if each.label() in self.adjective_types:
                        Object = each.leaves()
                        break
                # Get first noun in the tree
        self.pred_verb_phrase_siblings = None
        return {'object':Object}

    def get_predicate(self, sub_tree):
        """
        Returns the Verb along with its attributes, Also returns a Verb Phrase
        """

        sub_nodes = []
        sub_nodes = sub_tree.subtrees()
        sub_nodes = [each for each in sub_nodes if each.pos()]
        predicate = None
        pred_verb_phrase_siblings = []
        sub_tree  = ParentedTree.convert(sub_tree)
        for each in sub_nodes:
            if each.label() in self.verb_types:
                sub_tree = each
                predicate = each.leaves()

        #get all predicate_verb_phrase_siblings to be able to get the object
        sub_tree  = ParentedTree.convert(sub_tree)
        if predicate:
             pred_verb_phrase_siblings = self.tree_root.subtrees()
             pred_verb_phrase_siblings = [each for each in pred_verb_phrase_siblings if each.label() in ["NP","PP","ADJP","ADVP"]]
             self.pred_verb_phrase_siblings = pred_verb_phrase_siblings

        return {'predicate':predicate}

    def process_parse_tree(self,parse_tree):
        """
        Returns the Subject-Verb-Object Representation of a Parse Tree.
        Can Vary depending on number of 'sub-sentences' in a Parse Tree
        """
        self.tree_root = parse_tree
        # Step 1 - Extract all the parse trees that start with 'S'
        svo_list = [] # A List of SVO pairs extracted
        output_list = []
        output_dict ={}
        i=0

        for idx, subtree in enumerate(parse_tree[0].subtrees()):
            subject =None
            predicate = None
            Object = None
            if subtree.label() in ["S", "SQ", "SBAR", "SBARQ", "SINV", "FRAG"]:
                children_list = subtree
                children_values = [each_child.label() for each_child in children_list]
                children_dict = dict(zip(children_values,children_list))


                # Extract Subject, Verb-Phrase, Objects from Sentence sub-trees
                if children_dict.get("NP") is not None:
                    subject = self.get_subject(children_dict["NP"])

                if children_dict.get("VP") is not None:
                    # Extract Verb and Object
                    #i+=1
                    #"""
                    #if i==1:
                    #    pdb.set_trace()
                    #"""
                    predicate = self.get_predicate(children_dict["VP"])
                    Object = self.get_object(children_dict["VP"])

                try:
                    if subject['subject'] and predicate['predicate'] and Object['object']:
                        output_dict['subject'] = subject['subject']
                        output_dict['predicate'] = predicate['predicate']
                        output_dict['object'] = Object['object']
                        output_list.append(output_dict)
                except Exception as e:
                        print(e)
                        continue



        return output_list


    def traverse(self,t):
        try:
            t.label()
        except AttributeError:
            print(t)
        else:
            # Now we know that t.node is defined
            print('(', t.label())
            for child in t:
                traverse(child)

            print(')')

    def sentence_split(self,text):
        """
        returns the Parse Tree of a Sample
        """
        sentences = self.sent_detector.tokenize(text)
        return sentences


    def get_parse_tree(self,sentence):
        """
        returns the Parse Tree of a Sample
        """
        parse_tree = self.parser.raw_parse(sentence)

        return parse_tree

    def List_To_Tree(self,lst):
        if(not isinstance(lst, basestring)):
            if(len(lst) == 2 and isinstance(lst[0], basestring) and isinstance(lst[1], basestring)):
                lst = Tree(str(lst[0]).split('+')[0],[str(lst[1])])
            elif(isinstance(lst[0], basestring) and not isinstance(lst[1], basestring)):
                lst = Tree(str(lst[0]).split('+')[0],map(List_To_Tree, lst[1: len(lst) ]))
        return lst


if __name__=="__main__":
    svo = SVO()
    
    
    sentence = u'''Obama was born in Kenya. Obama has visited Kenya's president's birthplace. Non-native born Obama is taking our guns away. People who claim that Obama is born in Kenya are idiots. Obama claims to have been born in Honolulu. This story is a complete fabrication.'''
    sentences =  svo.sentence_split(sentence)
    val = []
    for sent in sentences:
        root_tree = svo.get_parse_tree(sent)
        val.append(svo.process_parse_tree(next(root_tree)))
    print(sentence)
    print(val)
    
    
    sentence = u'''Despite having been sentenced to 2 weeks’ jail for drink driving, \
state-owned public transport operator SMRT reserved an executive job placing \
for its Chief Operations Officer Alvin Kek. SMRT rallied it’s support for the \
military crony saying it has suspended his position while he serves his two weeks \
sentence. The COO is a former army colonel defended himself in court on Monday \
(Jun 25) saying that he was out drinking heavily with his friends at lavish country \
club, Temasek Club on April 20. Alvin Kek then left at about 2.30am and drove in the \
direction of Woodlands, and ended up at the Woodlands Checkpoint at 2.55am. According \
to a Chinese local newspaper, the married father of two children was found drunk with \
a China national woman in her 30s when he was stopped by the immigration officers. \
Immigration checkpoint officers hauled him up for a breath test and found he was \
nearly double the legal limit. According to court hearing, SMRT COO Alvin Kek is a \
repeat drink-driving offender, including other serious traffic offences like beating \
the red light and using a mobile phone during driving. Alvin Kek was among the 4 \
high-ranking military cronies brought on board SMRT after the former chief of defence \
force Desmond Kuek became CEO. A new chief of defence force will be taking over Desmond \
Kuek, but the military leadership has been a disaster for the public transport operator. \
Rail reliability is at its lowest in more than a decade, even after tens of billions \
were pumped into the MRT system.'''
    sentences =  svo.sentence_split(sentence)
    val = []
    for sent in sentences:
        root_tree = svo.get_parse_tree(sent)
        val.append(svo.process_parse_tree(next(root_tree)))
    print(sentence)
    print(val)
    


