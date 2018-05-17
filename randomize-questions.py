#----------------------------------------------------------
# Will Bowman
# 1/24/2018
#
# Randomize order of exam questions
#
#   Return new exam file and answer key
#   New exam file (*.tex) can be compiled to pdf
#
#----------------------------------------------------------
#
# assumes input exam files have suffix *.dat and are of format
#
# QQ question text
# AA (1) correct response...
# (2) resonse 2 ...
#
# assumes response (1) is correct response
# assumes at least two responses per question
# assumes incorrect responses of form (#), i.e.,
#   no characters before "(", and # element of set {1,2,3,4,5,...}
# assumes no empty lines within a question, i.e.,
#   after start of question line --> end of last response
# assumes at least one EMPTY line between questions, i.e.,
#   no whitespace!
# question or response can span multiple lines
#
# lines before / after exam questions will be preserved
#
#
#----------
#  USAGE
#----------
#
# run as `python randomize_questions.py -i <input-file>
#   option: `-o <name-modification-for-new-file>
#           default: *_shuffled.dat
#

left_header  = 'Astro 140, Spring 2018'
right_header = 'Unit Quiz 4'

### string to appear at beginning of exam
intro_statement = 'For each multiple choice question, select the best answer and bubble the corresponding letter on your scantron sheet.  For the final free response question, write your answer on the quiz booklet.  For multiple choice questions NVA means “Not a valid answer” and is never the correct choice.  If you have questions, you may raise your hand and ask the instructor or quiz proctor.  Otherwise, students are not allowed to give or receive information related to its contents during the in class unit quizzes. Students will be asked to sign a statement confirming this on the final page of the quiz. Finally, remember to write your name and student identification number on the first and last page of the quiz booklet and to bubble them into the scantron form.  '

### list of all statements to appear at end of exam
#final_lines = []
final_lines = ['\\noindent While taking this quiz, I did not give or receive information related to its contents (with the possible exception of clarifications by the instructor or exam proctor).',
               '\\bigskip',
               '\\noindent Signature $\\rule{6cm}{0.2mm}$ ']

# if False, responses are (1), (2), (3), ...
alphabetical_responses = True # False

# if False, leave AA prefix on correct responses
remove_AA = True # False

# if True, remove lines *beginning* with #
remove_comments = True
#!!! NOTE: TO EXTEND TO ALL COMMENTS, USE `line.replace('#', '%#') --> comment out of TeX

# if True, change QQ --> Q1, Q2, ..., Q10, ...
number_questions = True # False


#------------------------------------------------------------------------------

import numpy as np
import argparse as ap


def set_response(rindex, upper=True):

  rletter = chr(ord('a')+rindex)
  if upper:
    rletter = rletter.upper()
  return rletter



def parse_args(argv=None):
    """Parse the command line arguments

    Parameters
    ----------
    argv : list of string
        arguments to parse; if ``None``, ``sys.argv`` is used

    Returns
    -------
    Namespace
        parsed arguments
    """


    parser = ap.ArgumentParser(description='shuffle exam questions',
                            formatter_class=ap.RawTextHelpFormatter)

    parser.add_argument("-i","--finput", type=str, nargs='?',
                        help='''<input-file.dat>''',
                        default=None)

    parser.add_argument("-o","--output", type=str, nargs='?',
                        help='''output-file-suffix''',
                        default='_shuffled')

    args = parser.parse_args(args=argv)

    if args.finput is None:
        msg = 'Please fill in the input file'
        parser.error(msg)

    return args



def set_output(infile, suffix='_shuffled'):
  return infile[0:-4]+suffix+'.tex'


def set_respfile(outfile):
  return outfile[0:-4]+'-responses.dat'


def is_eof(f):
  'if no more questions, return TRUE'

  # get current position
  pos0 = f.tell()

  lines = f.readlines()
  eof = True
  for l in lines:
    if len(l)>2:
      if l[0:2]=='QQ':
        eof = False

  f.seek(pos0)

  return eof

def get_full_question(f):
  '''f is the test file object

     return a list of [Q, A1, A2,...]
     note: each item of list is a list containing each line of component'''

  header = []
  q = []
  resp = []

  line = '9753124680 get header lines'
  while line[0:2] != 'QQ':
    if line != '9753124680 get header lines':
      header.append(line)
    line = f.readline()

  while line[0:2] != 'AA':
    q.append(line)
    line = f.readline()

  resp1 = []
  while line[0:3] != '(2)':
    resp1.append(line)
    line = f.readline()
  resp.append(resp1)

  nline=2
  while line !='\n':
    resp_new = []
    while (line[0:2] != '('+str(nline+1)) & (line!='\n'):
      resp_new.append( line )
      line = f.readline()
    resp.append( resp_new )
    if line !='\n':
      nline += 1
        
  item = [header, q, resp]
  return item


def random_correct_index(qitem, resparr):
  '''qitem: list of question item, [header, question, response list]
     resparr: list of correct responses'''

  adjusted_list = []

  nresp = len(qitem[2])
  new_index = int(np.random.choice( np.linspace(0,nresp-1,nresp)  ))

#  print(new_index)

  if new_index != 0:
    adjusted_list.append( new_index )
    qcopy = qitem[2].copy()
    trade = qcopy[new_index]
    trade[0] = '(1)'+trade[0][3:]
    adjusted_correct = qcopy[0]
    resp_line = adjusted_correct[0]

    # numerical or alphabetical responses?
    if alphabetical_responses:
      resp = set_response( new_index )
    else:
      resp = str(new_index+1)

#    print([new_index, resp])

    # identify where correct response begins, i.e., (1)
    i=0
    char = 'A'
    while char != ')':
      i+=1
      char = resp_line[i]

    if remove_AA:
      adjusted_correct[0] = '('+resp+')'+adjusted_correct[0][i+1:]
    else:
      adjusted_correct[0] = adjusted_correct[0][0:i-2]+'('+resp+')'+adjusted_correct[0][i+1:]

    qitem[2][new_index] = adjusted_correct
    qitem[2][0] = trade
  else:
    adjusted_list.append( new_index )
    qcopy = qitem[2].copy()
    adjusted_correct = qcopy[0]
    resp_line = adjusted_correct[0]

    if alphabetical_responses:
      resp = set_response( new_index )
    else:
      resp = str(new_index+1)

    # identify where correct response begins, i.e., (1)
    i=0
    char = 'A'
    while char != ')':
      i+=1
      char = resp_line[i]

    if remove_AA:
      adjusted_correct[0] = '('+resp+')'+adjusted_correct[0][i+1:]
    else:
      adjusted_correct[0] = adjusted_correct[0][0:i-2]+'('+resp+')'+adjusted_correct[0][i+1:]

    qitem[2][new_index] = adjusted_correct


  qlist = qitem[2]

  # set desired response identifiers
  for q in qlist:
    if qlist.index(q) not in adjusted_list:
      if alphabetical_responses:
        resp = set_response( qlist.index(q) )
      else:
        resp = str(qlist.index(q)+1)
      q[0] = '('+resp+')'+q[0][3:]

  # update answer key
  if alphabetical_responses:
    resp_correct = set_response( new_index )
  else:
    resp_correct = str(new_index+1)
      
  resparr.append([len(resparr)+1, resp_correct])

def add_suffix(line, suffix= ' \\\\'):
#  print(repr(line))
  line += suffix
#  print(repr(line))
  return line

def write_question(qitem, fout, remove_comments=remove_comments):
  fout.write('\n')
  fout.write('\\begin{absolutelynopagebreak}')
  for part in qitem:
   for p in part:
    if type(p) is list:
      for q in p:
        q = add_suffix(q)
        if remove_comments:
          if q[0]!='#':
            fout.write(q)
        else:
          fout.write(q)
    else:
      p = add_suffix(p)
      if remove_comments:
        if p[0]!='#':
          fout.write(p)
      else:
        fout.write(p)
#      fout.write(p)
  fout.write('\\end{absolutelynopagebreak}')
  fout.write('\n')


def write_final_remarks(f, fout, remove_comments=remove_comments):
  '''write last items to new file
     fout: file object'''

  final = f.readlines()
  for l in final:
    l = add_suffix(l)
    if remove_comments:
      if l[0]!='#':
        fout.write(l)
    else:
      fout.write(l)

def write_tex_end(fout, lines=None):
  if not lines:
    line_list = ['\end{document}']
  else:
    line_list = ['','\\vfill']
    for l in lines:
      l = add_suffix(l)
      line_list.append(l)
    line_list.append('\end{document}')

  for l in line_list:
    fout.write('\n'+l)

def write_tex_header(fout, header=True):
  line_list = ['\documentclass[11pt]{article}',
               '\\usepackage[margin=1in]{geometry}',
               '\\usepackage[]{amsmath}',
               '\\newenvironment{absolutelynopagebreak}',
               '  {\par\\nobreak\\vfil\penalty0\\vfilneg',
               '   \\vtop\\bgroup}',
               '  {\par\\xdef\\tpd{\\the\prevdepth}\egroup',
               '   \prevdepth=\\tpd}', '']
  if header:
    line_list.append('\\usepackage{fancyhdr}')
    line_list.append('\pagestyle{fancy}')
    line_list.append('\\renewcommand{\headrulewidth}{1pt}')
    line_list.append('\\fancyhead[L]{'+left_header+'}')
    line_list.append('\\fancyhead[R]{'+right_header+'}')
    line_list.append('\\begin{document} \n')
  else:
    line_list.append('\\begin{document} \n')

  for l in line_list:
    fout.write('\n'+l)

def write_file_header(fout, more_text=None, length1=5, length2=3.5):
  head_list = ['\\noindent Name $\\rule{'+str(length1)+'cm}{0.2mm}$ '+\
               '\hfill Student ID $\\rule{'+str(length2)+'cm}{0.2mm}$'] 
  if more_text:
    addlines = ['', '\\bigskip',  more_text,'','\\bigskip',''] #,'','\\bigskip']
  else:
    addlines = ['', '\\bigskip','']
  for l in addlines:
    head_list.append(l)
  for l in head_list:
    fout.write('\n'+l) 


def print_listarr_to_file(arr, head='', fileout='',remove_par=False):
  "output a list of lists (2d array) to a file"
  np.set_printoptions(suppress=True, linewidth=20000)

  if fileout=='':
    f = input('Enter name of output file:\n')
  else:
    f = fileout

  if remove_par==False:
    resp_par = input("Remove apostrophes from strings? (y to accept)\n")
    if resp_par=='y':
      remove_par=True

  with open(f,'w') as infile:
    if head != '':
      infile.write('# ' + head + '\n#\n')
    for i in range(0,np.shape(arr)[0]):
      line = str(arr[i])
      line = line.replace("["," ")
      line = line.replace("]"," ")
      line = line.replace("("," ")
      line = line.replace(")"," ")
      line = line.replace(","," ")
      if remove_par==True:
        line = line.replace("'"," ")

      infile.write(line+'\n')


def write_response_file(resparr, respfout):
  '''resparr: list of responses
     respfout: name of output file'''

  print_listarr_to_file(resparr, head='QQ  correct', \
                        fileout=respfout,remove_par=True)



def main(argv=None):

  args = parse_args(argv)
  fnamein = args.finput
  fnameout = set_output(fnamein, suffix=args.output)
  respfout = set_respfile(fnameout) 

  with open(fnamein,'r') as fin:
    with open(fnameout,'w') as fout:

     write_tex_header(fout)
     write_file_header(fout, more_text=intro_statement)

     eof=False
     resparr = []
     while not eof:
       qitem = get_full_question(fin)
       random_correct_index(qitem, resparr)
       if number_questions:
         nquestion = len(resparr)
         qitem[1][0] = '\\noindent \\textbf{Question '+str(nquestion)+':} '+qitem[1][0][2:]
       write_question(qitem, fout)
       eof = is_eof(fin)

     fout.write('\n\pagebreak\n')
#     write_file_header(fout,more_text='\\textbf{Free Response Question:}')
     write_final_remarks(fin, fout)
     write_tex_end(fout, lines=final_lines)

     write_response_file(resparr, respfout)


if __name__ == '__main__':
  main()

