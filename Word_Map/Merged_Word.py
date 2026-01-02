#!/usr/bin/env python3
"""
Generate a list of all merged words from the word frequency analysis.
This script tracks words that were merged into canonical forms in Step 2 and Step 3.
"""
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

# Import constants and functions from process_all.py
# For standalone script, we'll duplicate them here
WORDS_TO_REMOVE = {
    'and', 'the', 'to', 'a', 'of', 'in', 'ct', 'that', 'this', 'is', 'by', 
    'for', 'on', 'can', 'et', 'al', 'are', 'an', 'with', 'what', 'which', 'or', 
    'not', 'p', 'out', 'use', 'so', 'was', 'such', 'into', 'has', 'from', 'how', 
    'though', 'have', 'its', 'e', 'also', 'about', 'based', 'them', 'one', 'been', 
    'must', 'do', 'just', 'i', 'term', 'csta', 'should', 'only', 'who', 'than', 
    'following', 'while', 'all', 'four', 'real', 'new', 'brennan', 'wing', 'first', 
    'many', 'cs', 'three', 'various', 'cuny', 'could', 'at', 'g', 'when', 'series', 
    'ways', 'her', 'will', 'core', 'every', 'school', 'well', 'parts', 'those', 
    'would', 'however', 'both', 'five', 'k', 'see', 'c', 'sub', 'sys', 'cansu', 
    'no', 'wide', 'users', 'early', 'ed', 'm', 'ng', 'any', 'aho', 'b', 'd', 
    'were', 'com', 'h', 'up', 'pro', 'lee', 'bers', 'add', 'tl', 'pp', 'er', 
    'big', 'sdgs', 'you', 'j', 'liu', 'ii', 'iii', 'y', 'good', 'single', 'sets', 
    'effec', 'n', 't', 'as', 'it', 's', 'way', 'defin', 'abil', 'we', 'they', 
    'carr', 'everyone', 'iste', 'stat', 'shute', 'applic', 'pea', 'barr', 'then', 
    'bett', 'oth', 'log', 'app', 'writ', 'there', 'evalu', 'lat', 'ord', 'pap', 
    'she', 'he', 'mean', 'refer', 'relat', 'simul', 'tion', 'selby', 'create', 
    'furth', 'glob', 'fine', 'some', 'our', 'jeanette', 'impl', 'nation', 'cent', 
    'reus', 'tak', 'error', 'addi', 'along', 'focu', 'eag', 'oft', 'cit', 'autom', 
    'soc', 'coin', 'flow', 'tedre', 'dr', 'argue', 'themselv', 'func', 'mak', 
    'issu', 'stud', 'valu', 'util', 'put', 'atten', 'non', 'vector', 'mas', 'shar', 
    'known', 'mere', 'spec', 'cipline', 'detec', 'his', 'stance', 'ref', 'among', 
    'resolu', 'scholar', 'upon', 'top', 'case', 'stage', 'dlc', 'item', 'hunsak', 
    'web', 'reduc', 'ason', 'hav', 'posi', 'act', 'six', 'f', 'un', 'asses', 'tang', 
    'wing', 're', 'publ', 'l', 'self', 'il', 'dell', 'thu', 'may', 'motiv', 'anoth', 
    'chos', 'nam', 'basi', 'dament', 'goe', 'even', 'pact', 'sec', 'rul', 'now', 
    'tsai', 'tem', 'fost', 'mcown', 'lot', 'eg', 'chang', 'isol', 'gramm', 'plac', 
    'numer', 'vast', 'dev', 'fix', 'ers', 'uation', 'stu', 'dent', 'pre', 'wang', 
    'voskoglou', 'buckley', 'ithm', 'u', 'lic', 'guzd', 'updat', 'vit', 'emerg', 
    'fo', 'rmulat', 'sult', 'rece', 'here', 'olv', 'succe', 'besid', 'divi', 'se', 
    'elaps', 'evolu', 'enrich', 'teract', 'theuse', 'suit', 'ctl', 'cronbach', 
    'alpha', 'coeff', 'ient', 'proble', 'ski', 'lls', 'icil', 'sengupta', 'tegrate', 
    'sykora', 'runn', 'answ', 'li', 'ttle', 'esssa', 'w', 'gp', 'o', 'mphas', 'r', 
    'serv', 'ces', 'ago', 'ated', 'scre', 'pac', 'trac', 'paper', 'rst', 'de', 
    'root', 'ned', 'anche', 'che', 'pensa', 'lle', 'lo', 'la', 'til', 'situ', 'etc', 
    'stephens', 'traini', 'sue', 'ar', 'main', 'intrins', 'bati', 'sfound', 'formu', 
    'prec', 'def', 'ini', 'pare', 'capac', 'feb', 'moreov', 'manag', 'deriv', 'loc', 
    'doe', 'tur', 'mim', 'kwon', 'bydraw', 'yadavet', 'thementalprocessforabstrac', 
    'yadav', 'der', 'mass', 'tc', 'yet', 'sort', 'prev', 'turn', 'amo', 'mus', 
    'unt', 'bate', 'sun', 'vice', 'mat', 'cover', 'st', 'uman', 'nt', 'nsf', 'x', 
    'off', 'nci', 'wave', 'tail', 'ique', 'box', 'equ', 'nine', 'ritt', 'omput', 
    'var', 'misse', 'tech', 'puter', 'wit', 'fac', 'whereas', 'ps', 'ychari', 'agre', 
    'begun', 'pd', 'if', 'java', 'python', 'gam', 'jam', 'evok', 'hsu', 'end',
    'yuan', 'possibilit', 'terdisciplinary', 'kale', 'want', 'dig', 'done', 'sense', 
    'prop', 'aid', 'acm', 'spac', 'seen', 'rea', 'son', 'chen', 'kim', 'tie', 
    'zhou', 'yi', 'center', 'webst', 'kersh', 'came', 'ctt', 'ching', 'snid', 
    'encounter', 'bundy', 'nucleu', 'itself', 'fig', 'giang', 'troduce', 'izing', 
    'albeit', 'underly', 'back', 'conqu', 'stephens', 'avail', 'fagerlund', 
    'araujo', 'tink', 'rapid', 'procur', 'mediante', 'dalla', 'possa', 'logo', 
    'uent', 'conclud', 'conjunc', 'third', 'inclus', 'agine', 'equal', 'will', 
    'deep', 'told', 'tell', 'silient', 'gett', 'kid', 'init', 'deci', 'uta', 
    'ide', 'ics', 'dicate', 'phy', 'ten', 'tract', 'let', 'say', 'typ', 'heurist', 
    'name', 'nest', 'event', 'rose', 'base', 'trigger', 'mann', 'furb', 'short', 
    'end', 'ccp', 'jam', 'gam', 'job', 'get', 'zha', 'mellon', 'ising', 'str', 
    'chamrat', 'empow', 'lem', 'prob', 'wichaya', 'remov', 'thinki', 'disjoin', 
    'summari', 'ach', 'tal', 'ya', 'sight', 'wheth', 'whole', 'ist', 'elucidate', 
    'zapata', 'latt', 'engin', 'honor', 'handle', 'always', 'plan', 'pillar', 
    'hand', 'concern', 'conc', 'phase', 'reflec', 'assess', 'age', 'still', 'took', 
    'much', 'somewhat', 'already', 'perhaps', 'someone', 'alone', 'behind', 'around', 
    'prior', 'previous', 'remain', 'shown', 'either', 'half', 'close', 'give', 
    'link', 'ibid', 'excerpt', 'article', 'book', 'journal', 'source', 'note', 'reference', 
    'vallance', 'towndrow', 'romero', 'rafiq', 'fraillon', 'papadaki', 'berland', 
    'wilensky', 'smith', 'kellow', 'park', 'carnegie', 'columbia', 'likert', 'survey', 
    'protein', 'biological', 'brain', 'machinery', 'political', 'economic', 'corporate', 
    'labor', 'childhood', 'eval', 'nrc', 'techni', 'que', 'andartific', 'characteriz', 
    'hybrid', 'constrict', 'spark', 'origin', 'combine', 'adequate', 'formal', 'socio', 
    'separat', 'gather', 'feel', 'interconnection', 'likelihood', 'tendency', 'am', 'fourth', 
    'regulat', 'metacognit', 'suscept', 'analytical', 'seminate', 'feedback', 'processi', 
    'continu', 'capabilit', 'debat', 'resort', 'mind', 'snap', 'offshoot', 'dialogue', 
    'contain', 'strength', 'citizen', 'trend', 'centur', 'advanc', 'traditional', 'strong', 
    'excellent', 'quick', 'member', 'cooperate', 'labour', 'aggregate', 'recommendation', 
    'analyzingdata', 'visual', 'breadth', 'pth', 'programmer', 'calculat', 'change', 
    'curricula', 'increasing', 'shape', 'manipulat', 'academic', 'agree', 'description', 
    'eventual', 'ring', 'mindstorm', 'earn', 'share', 'generalis', 'fundamentalto', 'expand', 
    'relaunch', 'reviv', 'influent', 'guidelin', 'entitl', 'sole', 'anxiety', 'pair', 'young', 
    'primary', 'part', 'art', 'simplify', 'transpos', 'access', 'simultaneous', 'compar', 
    'scientif', 'offer', 'opportun', 'enable', 'occur', 'cur', 'decad', 'increas', 'influenc', 
    'endeavour', 'built', 'ventor', 'platform', 'application', 'terface', 'display', 'socializ', 
    'concrete', 'exampl', 'scaffold', 'professional', 'categoriz', 'categor', 'pract', 'levant', 
    'theoretical', 'robust', 'transferabil', 'synthesi', 'evaluation', 'correc', 'gestur', 
    'promulgat', 'ective', 'associat', 'compris', 'siamo', 'convinti', 'prima', 'approssimazione', 
    'significato', 'espressione', 'formatico', 'essere', 'sufficientemente', 'chiarito', 
    'spiegazione', 'ferenziale', 'sieme', 'competenze', 'mentali', 'ottenute', 'studio', 
    'pratica', 'formatica', 'speak', 'individu', 'evaluate', 'theoret', 'consid', 'intellectu', 
    'multidimension', 'decid', 'frequent', 'cooperat', 'unravel', 'skillful', 'tricate', 'transl', 
    'hu', 'man', 'lin', 'aiot', 'investigat', 'robotic', 'hypothesiz', 'ventory', 'enjoy', 
    'predictor', 'characteris', 'especiallyfollowingjeannettew', 'educa', 'competence', 'expect', 
    'activate', 'memory', 'connection', 'certainty', 'articulate', 'comprehensib', 'hardware', 
    'arrange', 'convey', 'newell', 'fab', 'accomplish', 'thereaft', 'crease', 'harmony', 
    'localit', 'sustain', 'globe', 'mediate', 'scope', 'ambit', 'monstrate', 'applicabil', 
    'postulat', 'grand', 'compat', 'portance', 'pedagog', 'designingsystem', 
    'andunderstandinghumanbehavior', 'instructor', 'intentional', 'correspondence', 'circuit', 
    'algebra', 'capture', 'feas', 'render', 'infeas', 'network', 'strategy', 'curriculum', 
    'characterization', 'diverse', 'dependent', 'referr', 'range', 'stress', 'handl', 'cacer', 
    'elevate', 'expectation', 'organization', 'strand', 'scratchjr', 'math', 'contribu', 'hope', 
    'biolog', 'refin', 'asbell', 'clarke', 'combination', 'obtain', 'material', 'computational', 
    'establish', 'succinct', 'content', 'great', 'divers', 'beginn', 'assessment', 'efficacy', 
    'foster', 'fundam', 'ormulat', 'message', 'necessitat', 'curre', 'uting', 'purpos', 'theory', 
    'fund', 'itiate', 'thinker', 'computationalthinker', 'ignor', 'relevant', 'solver', 
    'brainstorm', 'referenc', 'convert', 'cycle', 'compete', 'conduct', 'levance', 'portray', 
    'exclusiv', 'modern', 'formatt', 'insight', 'featur', 'philosophy', 'innovat', 'side', 
    'summariz', 'critique', 'burgeon', 'plann', 'standl', 'pewkam', 'bruke', 'roadmap', 
    'uction', 'demyst', 'nology', 'turhan', 'peracaula', 'bosch', 'reignit', 'certain', 
    'perseverance', 'captur', 'generation', 'chairman', 'disassemb', 'popular', 'similarit', 
    'telligent', 'familiar', 'vestigate', 'quiry', 'exhibit', 'explor', 'verse', 'mindread', 
    'entry', 'ciplinary', 'persever', 'chevali', 'observation', 'constitute', 'discov', 'capabil', 
    'believe', 'transvers', 'csizmadia', 'flect', 'modif', 'effectivel', 'variablesand', 
    'falloon', 'computa', 'function', 'makin', 'articl', 'exploit', 'preven', 'workspac', 
    'centr', 'simplific', 'media', 'summary', 'zhen', 'style', 'activi', 'basical', 'quantific', 
    'ductionism', 'problemat', 'epistem', 'logic', 'finding', 'research', 'mainstream', 
    'specializ', 'justific', 'necessitate', 'populari', 'encourag', 'labell', 'equipp', 
    'investig', 'reproduc', 'perfect', 'silience', 'benefic', 'encompas', 'framing', 
    'participate', 'communit', 'decision', 'unit', 'indicat', 'recognis', 'creative', 
    'anderson', 'modell', 'credit', 'commun', 'dai', 'kafai', 'youth', 'haseski', 
    'qual', 'collec', 'easi', 'measure', 'over', 'participant', 'propose', 'assign', 
    'leverag', 'tolerance', 'open', 'language', 'place', 'remix', 'initial', 'technique', 
    'charact', 'lack', 'mention', 'processor', 'span', 'opportunit', 'outlin', 'increment', 
    'korkmaz', 'recent', 'volve', 'taught', 'abilit', 'snyd', 'tive', 'list', 'symbol', 
    'dustry', 'educator', 'transf', 'before', 'similar', 'drawn', 'march', 'bcomput', 
    'palt', 'pedaste', 'inconsistent', 'facet', 'komm', 'confu', 'guid', 'adopt', 
    'interac', 'potent', 'sponse', 'board', 'acquisi', 'stag', 'embedd', 'mindset', 
    'quire', 'table', 'designer', 'servic', 'operator', 'disposition', 'online', 'pathway', 
    'colleagu', 'instruc', 'extens', 'gain', 'college', 'revisit', 'orient', 'factor', 
    'recogn', 'bocconi', 'umbrella', 'embod', 'arise', 'challeng', 'brought', 'languag', 
    'grade', 'clarif', 'initiativ', 'acquire', 'subsequent', 'account', 'receiv', 'seek', 
    'serve', 'rel', 'each', 'simple', 'propert', 'expense', 'bear', 'search', 'user', 
    'fun', 'communication', 'replic', 'everyday', 'talent', 'depart', 'lesson', 'biology', 
    'train', 'seeming', 'cas', 'comp', 'take', 'final', 'according', 'informatic', 'revis', 
    'expert', 'nouri', 'discuss', 'cours', 'machin', 'artific', 'two', 'mcowan', 'choos', 
    'explicit', 'stead', 'complicat', 'subject', 'select', 'composi', 'discus', 'spite', 
    'reformulat', 'generat', 'team', 'collect', 'skillset', 'play', 'environment', 
    'integrat', 'constitut', 'classroom', 'appear', 'interact', 'target', 'resolv', 
    'major', 'cre', 'posit', 'workshop', 'project', 'synthesiz', 'mechanism', 'tackl', 
    'attempt', 'high', 'correct', 'clear', 'bring', 'council', 'inter', 'systematical', 
    'denn', 'techn', 'scribe', 'find', 'achiev', 'terpret', 'variabl', 'predic', 'conceptu', 
    'future', 'numb', 'riddle', 'telligence', 'answer', 'point', 'child', 'manage', 'essent', 
    'therefore', 'semin', 'although', 'able', 'multiple', 'situation', 'rath', 'game', 'same', 
    'because', 'curzon', 'betwe', 'figure', 'thing', 'scor', 'argu', 'year', 'word', 'object', 
    'technolog', 'detail', 'accept', 'identif', 'engag', 'promot', 'deal', 'transform', 'follow', 
    'aim', 'action', 'look', 'explain', 'where', 'methodology', 'builder', 'virtu', 'natur', 
    'seymour', 'twenty', 'face', 'emphasi', 'typical', 'sever', 'successful', 'contextual', 
    'partial', 'complet', 'predict', 'vpython', 'constant', 'statement', 'calculate', 'complete', 
    'routine', 'momentum', 'low', 'middle', 'confidence', 'ambigu', 'collabor', 'without', 
    'assistance', 'specifical', 'laid', 'time', 'vision', 'topic', 'provide', 'type', 'made', 
    'practice', 'state', 'condi', 'addres', 'said', 'publish', 'effort', 'kalelioglu', 'learner', 
    'secondary', 'original', 'habit', 'ing', 'competency', 'reflect', 'come', 'elementary', 
    'software', 'explore', 'paradigm', 'facilitate', 'devic', 'produce', 'massachusett', 'issue', 
    'generate', 'professor', 'identific', 'surround', 'standard', 'try', 'highlight', 'proctor', 
    'entail', 'adapt', 'sent', 'compose', 'lead', 'product', 'course', 'formula', 'communicat', 
    'produc', 'organ', 'difficult', 'domain', 'comple', 'class', 'recogniz', 'emphasiz', 'empower', 
    'employ', 'achieve', 'emphasis', 'performance', 'creat', 'artifact', 'associ', 'analyz', 'cod', 
    'poss', 'dimen', 'portant', 'ment', 'bas', 'strateg', 'ques', 'mathemat', 'iter', 'iterat', 
    'structur', 'derstood', 'acros', 'posses', 'arithmet', 'analysi', 'attitud', 'competenc', 
    'measur', 'univers', 'consist', 'sequenc', 'disciplin', 'principl', 'resourc', 'activ', 
    'childr', 'conceptualiz', 'perspect', 'techniqu', 'formul', 'mathematic', 
    'analys', 'consensu', 'introduc', 'integr', 'interpret', 'transferr', 'creativ', 'collaborat', 
    'comprehens', 'comprehend', 'creat', 'be', 'their', 'these', 'using', 'through', 'but', 
    'more', 'most', 'us', 'like', 'within', 'other', 'same', 'because', 'although', 'therefore', 
    'where', 'without', 'before', 'after', 'each', 'over', 'under', 'between', 'around', 'today', 
    'current', 'since', 'year', 'century', 'world', 'life', 'people', 'individual', 'kind', 'thing', 
    'area', 'field', 'level', 'form', 'set', 'order', 'state', 'type', 'particular', 'general', 
    'common', 'different', 'variety', 'exist', 'become', 'found', 'used', 'make', 'take', 'bring', 
    'build', 'help', 'work', 'look', 'draw', 'carry', 'come', 'give', 'need', 'know', 'learn', 
    'read', 'write', 'present', 'provide', 'allow', 'address', 'support', 'focus', 'result', 
    'example', 'question', 'answer', 'view', 'point', 'goal', 'aspect', 'element', 'component', 
    'factor', 'notion', 'concept', 'idea', 'comput', 'solv', 'defini', 'derstand', 'velop', 
    'ident', 'clude', 'oper', 'crit', 'digit', 'recogni', 'specif', 'appl', 'analyt', 'unambigu', 
    'simpl', 'maximi', 'execu', 'iter', 'believ', 'jeannette', 'papert', 'stephenson', 'weintrop', 
    'grov', 'snick', 'woollard', 'be', 'their', 'these', 'using', 'through', 'but', 'more', 
    'most', 'same', 'because', 'although', 'therefore', 'where', 'over', 'down', 'within', 'being', 
    'definition', 'universal', 'large', 'small', 'key', 'reason', 'suggest', 'regard', 'appropriate', 
    'necessary', 'educ', 'include', 'step', 'expres', 'study', 'task', 'require', 'enabl', 'combin', 
    'activist', 'author', 'mobile', 'block', 'beyond', 'optim', 'fail', 'divid', 'subtask', 
    'failure', 'connect', 'confront', 'characteristic', 'engage', 'scratch', 'force', 'update', 
    'identify', 'limit', 'populariz', 'break', 'requir', 'intern', 'propos', 'broad', 'activit', 
    'teach', 'includ', 'practic', 'thought', 'involv', 'sign', 'inform', 'student', 'teacher', 
    'perspectiv', 'literature', 'compos', 'problem', 'problems', 'solve', 'solving', 'solv', 
    'solu', 'solution',     'solutions', 'think', 'process', 'proces', 'processes', 'skill', 'skills', 
    'science', 'human', 'understand', 'derstand', 'understanding', 'approach', 'effective', 'complex', 
    'method', 'context', 'consider', 'knowledge', 'attitude', 'effect', 'perform', 'scientist', 
    'engineer', 'researcher', 'society', 'technology', 'stem', 'literacy', 'describ', 'develop', 
    'provid', 'utiliz', 'apply', 'organize', 'encompass', 'framework', 'dimension', 'taxonomy', 
    'complement', 'tool', 'code', 'test', 'troubleshoot', 'machine', 'motion', 'structure', 
    'structur', 'structures', 'systemat', 'design', 'designing', 'operational', 'unambiguous', 
    'unambigu', 'formulate', 'formulat', 'formulating', 'fundament', 'fundamental', 'behavior', 
    'behaviour', 'cognit', 'express', 'conceptual', 'construct', 'organiz', 'procedur'
}
# Normalize all to lowercase for consistent matching
WORDS_TO_REMOVE = {w.lower().strip() for w in WORDS_TO_REMOVE}

# Word merging rules: map variants to canonical forms
WORD_MERGE_MAP = {
    # abstraction variants
    'abstraction': 'abstraction', 'abstrac': 'abstraction', 'abstract': 'abstraction',
    # representation variants
    'representation': 'representation', 'represent': 'representation',
    # program variants
    'program': 'program', 'programm': 'program', 'programming': 'program',
    # computation variants
    'computation': 'computation', 'comput': 'computation', 'computational': 'computation',
    # decomposition variants
    'decomposition': 'decomposition', 'decomposi': 'decomposition', 'decompos': 'decomposition', 
    'deconstruc': 'decomposition', 'deconstruct': 'decomposition',
    # recursion variants
    'recursion': 'recursion', 'iterative': 'recursion', 'recur': 'recursion', 'recurs': 'recursion', 
    'recursive': 'recursion', 'iteration': 'recursion',
    # automation variants
    'automation': 'automation', 'automat': 'automation', 'automate': 'automation', 
    'automatical': 'automation', 'auto': 'automation',
    # execute variants
    'execute': 'execute', 'execut': 'execute', 'execu': 'execute', 'executing': 'execute',
    # optimization variants
    'optimization': 'optimization', 'optim': 'optimization', 'maximi': 'optimization', 
    'minimum': 'optimization', 'optimize': 'optimization',
    # analyze variants
    'analyze': 'analyze', 'analys': 'analyze', 'analyt': 'analyze', 'analysis': 'analyze',
    # efficiency variants
    'efficiency': 'efficiency', 'efficient': 'efficiency',
    # simulation variants
    'simulation': 'simulation', 'simulat': 'simulation', 'simulate': 'simulation',
    # sequence variants
    'sequence': 'sequence', 'sequenc': 'sequence', 'sequencing': 'sequence',
    # operationalization variants
    'operationalization': 'operationalization', 'operationaliz': 'operationalization', 
    'operationalis': 'operationalization',
    # algorithm variants
    'algorithm': 'algorithm', 'algor': 'algorithm', 'algorithms': 'algorithm', 'algorithmic': 'algorithm',
    # pattern-recognition variants
    'pattern-recognition': 'pattern-recognition', 'pattern': 'pattern-recognition', 'patterns': 'pattern-recognition',
    'recognition': 'pattern-recognition', 'patternrecognition': 'pattern-recognition', 
    'pattern_recognition': 'pattern-recognition',
    # generalization variants
    'generalization': 'generalization', 'generaliz': 'generalization', 'generalizations': 'generalization',
}

def merge_word(word):
    """Merge word variants to canonical forms"""
    word_lower = word.lower().strip()
    
    # Check exact match first
    if word_lower in WORD_MERGE_MAP:
        return WORD_MERGE_MAP[word_lower]
    
    # Check if word starts with any variant (for partial matches like "solving" -> "solve")
    # Sort by length (longest first) to match most specific variants first
    sorted_variants = sorted(WORD_MERGE_MAP.items(), key=lambda x: len(x[0]), reverse=True)
    for variant, canonical in sorted_variants:
        if word_lower.startswith(variant) and len(variant) >= 3:  # Only for substantial matches
            return canonical
    
    return word_lower

def simple_stem(word):
    """Remove common suffixes and prefixes"""
    if len(word) <= 2:
        return word.lower()
    
    word_lower = word.lower()
    
    # Common suffixes (longest first)
    suffixes = [
        'ization', 'isation', 'ational', 'fulness', 'ousness', 'iveness',
        'tional', 'biliti', 'ation', 'alism', 'aliti', 'ement', 'enci', 
        'anci', 'izer', 'iser', 'ator', 'alli', 'ousli', 'entli', 'eli', 
        'bli', 'ing', 'ed', 'er', 'est', 'ly', 'tion', 'sion', 'ness', 
        'ment', 'ity', 'ies', 'ied', 'es', 's', 'al', 'ial', 'ical',
        'able', 'ible', 'ful', 'less', 'ive', 'ous', 'ious', 'eous',
        'ize', 'ise', 'ify', 'fy', 'en', 'ic'
    ]
    
    suffixes.sort(key=len, reverse=True)
    
    for suffix in suffixes:
        if word_lower.endswith(suffix) and len(word_lower) > len(suffix) + 2:
            stemmed = word_lower[:-len(suffix)]
            if len(stemmed) >= 2:
                return stemmed
    
    # Remove common prefixes
    prefixes = ['un', 're', 'pre', 'dis', 'mis', 'over', 'out', 'under', 'de', 'in', 'im', 'il', 'ir', 'non']
    for prefix in prefixes:
        if word_lower.startswith(prefix) and len(word_lower) > len(prefix) + 2:
            stemmed = word_lower[len(prefix):]
            if len(stemmed) >= 2:
                return stemmed
    
    return word_lower

def extract_words(text):
    """Extract words from text"""
    if not text:
        return []
    
    # Convert to lowercase and remove special characters
    text = text.lower()
    # Keep only alphanumeric and spaces
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Split into words
    words = text.split()
    # Filter out very short words and numbers
    words = [w for w in words if len(w) >= 2 and not w.isdigit()]
    
    return words

def main():
    # Paths
    base_dir = Path(__file__).parent
    json_file = base_dir.parent / 'V2' / 'matched_papers_with_relevant_text.json'
    output_file = base_dir / 'word_frequency_analysis_merged_words.txt'
    
    if not json_file.exists():
        print(f"Error: JSON file not found: {json_file}")
        return
    
    print("Reading JSON data...")
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract all relevant text from matched papers
    print("Extracting words from relevant text...")
    all_words = []
    matched_papers = data.get('matched_papers', [])
    
    for paper in matched_papers:
        relevant_text = paper.get('relevant_text', '')
        if relevant_text and relevant_text != "None":
            words = extract_words(relevant_text)
            all_words.extend(words)
    
    print(f"Total words extracted: {len(all_words):,}")
    
    # Step 1: Count raw word frequencies
    word_freq_raw = Counter(all_words)
    sorted_raw = sorted(word_freq_raw.items(), key=lambda x: x[1], reverse=True)
    total_words = sum(word_freq_raw.values())
    
    print(f"Unique words (raw): {len(word_freq_raw):,}")
    print(f"Total word count: {total_words:,}")
    
    # Step 2: Track merged words
    print("\nStep 2: Tracking merged word variants...")
    
    # Track merges: canonical_form -> {variants: [(original, freq), ...], total_freq: int}
    merged_words_step2 = defaultdict(lambda: {'canonical': '', 'variants': [], 'total_freq': 0})
    
    # First pass: collect all words and their merged forms
    word_to_merged = {}
    for word, freq in sorted_raw:
        merged = merge_word(word)
        word_lower = word.lower().strip()
        merged_lower = merged.lower().strip()
        word_to_merged[word] = (merged, merged_lower)
    
    # Second pass: group all variants by their canonical form
    for word, freq in sorted_raw:
        merged, merged_lower = word_to_merged[word]
        
        # Only track if this canonical form is in the merge map (has variants defined)
        if merged_lower in WORD_MERGE_MAP.values():
            if not merged_words_step2[merged_lower]['canonical']:
                merged_words_step2[merged_lower]['canonical'] = merged
            
            # Add this variant if not already present
            if not any(v[0] == word for v in merged_words_step2[merged_lower]['variants']):
                merged_words_step2[merged_lower]['variants'].append((word, freq))
                merged_words_step2[merged_lower]['total_freq'] += freq
            else:
                # Update frequency if variant already exists
                for i, (v_word, v_freq) in enumerate(merged_words_step2[merged_lower]['variants']):
                    if v_word == word:
                        merged_words_step2[merged_lower]['variants'][i] = (word, v_freq + freq)
                        merged_words_step2[merged_lower]['total_freq'] += freq
                        break
    
    # Sort by total frequency
    merged_words_step2_sorted = sorted(
        merged_words_step2.items(), 
        key=lambda x: x[1]['total_freq'], 
        reverse=True
    )
    
    print(f"  Found {len(merged_words_step2_sorted):,} canonical forms with merged variants")
    
    # Step 3: Track merges after stemming
    print("\nStep 3: Tracking merged words after stemming...")
    
    # Get words that passed Step 2 (not removed)
    filtered_words = []
    merged_freq = Counter()
    for word, freq in sorted_raw:
        merged = merge_word(word)
        merged_freq[merged] += freq
    
    for word, freq in merged_freq.items():
        word_lower = word.lower().strip()
        if word_lower not in WORDS_TO_REMOVE:
            filtered_words.append((word, freq))
    
    merged_words_step3 = defaultdict(lambda: {'canonical': '', 'variants': [], 'total_freq': 0})
    
    # Track words that get merged after stemming
    for word, freq in filtered_words:
        stemmed = simple_stem(word)
        stemmed_lower = stemmed.lower().strip()
        
        # Apply merge again after stemming
        merged_stemmed = merge_word(stemmed_lower)
        merged_stemmed_lower = merged_stemmed.lower().strip()
        
        # Track if the final merged form is a canonical form with variants
        # and is different from the original word
        word_lower = word.lower().strip()
        if (merged_stemmed_lower in WORD_MERGE_MAP.values() and 
            word_lower != merged_stemmed_lower):
            if not merged_words_step3[merged_stemmed_lower]['canonical']:
                merged_words_step3[merged_stemmed_lower]['canonical'] = merged_stemmed
            
            # Add this variant if not already present
            if not any(v[0] == word for v in merged_words_step3[merged_stemmed_lower]['variants']):
                merged_words_step3[merged_stemmed_lower]['variants'].append((word, merged_stemmed, freq))
                merged_words_step3[merged_stemmed_lower]['total_freq'] += freq
            else:
                # Update frequency if variant already exists
                for i, (v_word, v_stemmed, v_freq) in enumerate(merged_words_step3[merged_stemmed_lower]['variants']):
                    if v_word == word:
                        merged_words_step3[merged_stemmed_lower]['variants'][i] = (word, merged_stemmed, v_freq + freq)
                        merged_words_step3[merged_stemmed_lower]['total_freq'] += freq
                        break
    
    # Sort by total frequency
    merged_words_step3_sorted = sorted(
        merged_words_step3.items(), 
        key=lambda x: x[1]['total_freq'], 
        reverse=True
    )
    
    print(f"  Found {len(merged_words_step3_sorted):,} additional merges after stemming")
    
    # Write merged words file
    print(f"\nWriting merged words list: {output_file}")
    merged_lines = []
    merged_lines.append("=" * 80)
    merged_lines.append("MERGED WORDS - COMPLETE LIST")
    merged_lines.append("=" * 80)
    merged_lines.append("")
    merged_lines.append("This file shows all word variants that were merged into canonical forms.")
    merged_lines.append("")
    
    # Step 2 merged words
    merged_lines.append("STEP 2: WORDS MERGED AFTER INITIAL PROCESSING")
    merged_lines.append("-" * 80)
    merged_lines.append(f"Total canonical forms: {len(merged_words_step2_sorted):,}")
    merged_lines.append("")
    
    for canonical, data in merged_words_step2_sorted:
        merged_lines.append(f"Canonical Form: {data['canonical']}")
        merged_lines.append(f"  Total Frequency: {data['total_freq']:,}")
        merged_lines.append(f"  Variants ({len(data['variants'])}):")
        
        # Sort variants by frequency
        variants_sorted = sorted(data['variants'], key=lambda x: x[1], reverse=True)
        for variant, freq in variants_sorted:
            merged_lines.append(f"    - {variant:<30} (freq: {freq:,})")
        merged_lines.append("")
    
    merged_lines.append("")
    merged_lines.append("")
    
    # Step 3 merged words
    merged_lines.append("STEP 3: WORDS MERGED AFTER STEMMING")
    merged_lines.append("-" * 80)
    merged_lines.append(f"Total canonical forms: {len(merged_words_step3_sorted):,}")
    merged_lines.append("")
    
    for canonical, data in merged_words_step3_sorted:
        merged_lines.append(f"Canonical Form: {data['canonical']}")
        merged_lines.append(f"  Total Frequency: {data['total_freq']:,}")
        merged_lines.append(f"  Variants ({len(data['variants'])}):")
        
        # Sort variants by frequency
        variants_sorted = sorted(data['variants'], key=lambda x: x[2], reverse=True)
        for original, stemmed, freq in variants_sorted:
            merged_lines.append(f"    - {original:<25} -> {stemmed:<25} (freq: {freq:,})")
        merged_lines.append("")
    
    merged_lines.append("")
    merged_lines.append("=" * 80)
    merged_lines.append("SUMMARY")
    merged_lines.append("=" * 80)
    merged_lines.append(f"Total canonical forms in Step 2: {len(merged_words_step2_sorted):,}")
    merged_lines.append(f"Total canonical forms in Step 3: {len(merged_words_step3_sorted):,}")
    
    total_freq_step2 = sum(d['total_freq'] for _, d in merged_words_step2_sorted)
    total_freq_step3 = sum(d['total_freq'] for _, d in merged_words_step3_sorted)
    merged_lines.append(f"Total frequency merged in Step 2: {total_freq_step2:,}")
    merged_lines.append(f"Total frequency merged in Step 3: {total_freq_step3:,}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(merged_lines))
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total canonical forms in Step 2: {len(merged_words_step2_sorted):,}")
    print(f"Total canonical forms in Step 3: {len(merged_words_step3_sorted):,}")
    print(f"Total frequency merged in Step 2: {total_freq_step2:,}")
    print(f"Total frequency merged in Step 3: {total_freq_step3:,}")
    print(f"\nOutput file: {output_file}")
    print("\n✓ Merged words file generated successfully!")

if __name__ == '__main__':
    main()
