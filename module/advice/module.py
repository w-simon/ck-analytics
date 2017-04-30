#
# Collective Knowledge (universal advice about experiments, bugs, models, 
#                       features, optimizations, adaptation, 
#                       community remarks ...)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings

hextra='<i><center>\n'
hextra+='This is a community-driven R&D: \n'
hextra+=' [ <a href="http://cKnowledge.org/ai">collaborative AI optimization</a> ], '
hextra+=' [ <a href="https://github.com/dividiti/ck-caffe">CK-Caffe</a> ], '
hextra+=' [ <a href="https://github.com/ctuning/ck-tensorflow">CK-TensorFlow</a> ], '
hextra+=' [ <a href="https://en.wikipedia.org/wiki/Collective_Knowledge_(software)">CK intro</a>, \n'
hextra+='CK papers: <a href="https://www.researchgate.net/publication/304010295_Collective_Knowledge_Towards_RD_Sustainability">1</a> and \n'
hextra+='<a href="https://arxiv.org/abs/1506.06256">2</a>; \n'
hextra+='<a href="https://www.youtube.com/watch?v=Q94yWxXUMP0">YouTube intro</a> ] \n'
hextra+='</center></i>\n'
hextra+='<br>\n'

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# access available CK-AI self-optimizing functions

def show(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    h=''
    h+='<center>\n'
    h+='\n\n<script language="JavaScript">function copyToClipboard (text) {window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);}</script>\n\n' 

#    h+='<h2>Aggregated results from Caffe crowd-benchmarking (time, accuracy, energy, cost, ...)</h2>\n'

    h+=hextra

    # Check host URL prefix and default module/action
    rx=ck.access({'action':'form_url_prefix',
                  'module_uoa':'wfe',
                  'host':i.get('host',''), 
                  'port':i.get('port',''), 
                  'template':i.get('template','')})
    if rx['return']>0: return rx
    url0=rx['url']
    template=rx['template']

    url=url0
    action=i.get('action','')
    muoa=i.get('module_uoa','')

    st=''

    url+='action=index&module_uoa=wfe&native_action='+action+'&'+'native_module_uoa='+muoa
    url1=url


    h+=url

    return {'return':0, 'html':h, 'style':st}
