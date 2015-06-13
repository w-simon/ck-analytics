#
# Collective Knowledge (various graphs for experiment)
#
# See CK LICENSE.txt for licensing details
# See CK Copyright.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://cTuning.org/lab/people/gfursin
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
var_post_subgraph='subgraph'
var_post_cur_subgraph='cur_subgraph'
var_post_tmp_graph_file='graph_tmp_file'
var_post_refresh_graph='refresh_graph'
var_post_reset_graph='reset_graph'
var_post_autorefresh='graph_autorefresh'
var_post_autorefresh_time='graph_autorefresh_time'

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
# plot universal graph by flat dimensions

def plot(i):
    """

    Input:  {
              (load_table_from_file)                     - load table directly from file
                         or
              Select entries or table:
                 (repo_uoa) or (experiment_repo_uoa)     - can be wild cards
                 (remote_repo_uoa)                       - if remote access, use this as a remote repo UOA
                 (module_uoa) or (experiment_module_uoa) - can be wild cards
                 (data_uoa) or (experiment_data_uoa)     - can be wild cards

                 (repo_uoa_list)                       - list of repos to search
                 (module_uoa_list)                     - list of module to search
                 (data_uoa_list)                       - list of data to search

                 (search_dict)                         - search dict
                 (ignore_case)                         - if 'yes', ignore case when searching

                       OR 

                 table                                 - experiment table (if drawing from other functions)


              (flat_keys_list)                      - list of flat keys to extract from points into table
                                                      (order is important: for example, for plot -> X,Y,Z)

              (flat_keys_list_separate_graphs)      - [ [keys], [keys], ...] - several graphs ...

              (labels_for_separate_graphs)          - list of labels for separate graphs

              (flat_keys_index)                     - add all flat keys starting from this index 
              (flat_keys_index_end)                 - add all flat keys ending with this index (default #min)

              (out_to_file)                         - save picture to file, if supported
              (out_to_file_repo_uoa)                - repo uoa where to save file (when reproducing graphs for interactive articles)
              (out_to_file_module_uoa)              - module uoa where to save file (when reproducing graphs for interactive articles)
              (out_to_file_data_uoa)                - data uoa where to save file (when reproducing graphs for interactive articles)

              (save_table_to_json_file)             - save table to json file

              Graphical parameters:
                plot_type                  - mpl_2d_scatter
                point_style                - dict, setting point style for each separate graph {"0", "1", etc}

                x_ticks_period             - (int) for bar graphs, put periodicity when to show number 


            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os

    o=i.get('out','')

    pst=i.get('point_style',{})

    otf=i.get('out_to_file','')
    otf_ruoa=i.get('out_repo_uoa','')
    otf_muoa=i.get('out_module_uoa','')
    otf_duoa=i.get('out_data_uoa','')

    xtp=i.get('x_ticks_period','')
    if xtp=='' or xtp==0: xtp=1
    if xtp!='': xtp=int(xtp)

    lsg=i.get('labels_for_separate_graphs',[])

    stjf=i.get('save_table_to_json_file','')

    table=i.get('table',[])

    ltfj=i.get('load_table_from_file','')
    if ltfj!='':
       rx=ck.load_json_file({'json_file':ltfj})
       if rx['return']>0: return rx
       table=rx['dict']

    # Check if table already there
    if len(table)==0:
       # Get table from entries
       tmp_a=i.get('action','')
       tmp_mu=i.get('module_uoa','')

       i['action']='get'
       i['module_uoa']=cfg['module_deps']['experiment']

       r=ck.access(i)
       if r['return']>0: return r

       table=r['table']

       rk=r['real_keys']

       i['action']=tmp_a
       i['module_uoa']=tmp_mu
    else:
       # If sort/substitute

       si=i.get('sort_index','')
       if si!='':
          rx=ck.access({'action':'sort_table', 
                        'module_uoa':cfg['module_deps']['experiment'], 
                        'table':table, 
                        'sort_index':si})
          if rx['return']>0: return rx
          table=rx['table']

       # Substitute all X with a loop (usually to sort Y and compare with predictions in scatter graphs, etc)
       if i.get('substitute_x_with_loop','')=='yes':
          rx=ck.access({'action':'substitute_x_with_loop', 
                        'module_uoa':cfg['module_deps']['experiment'], 
                        'table':table})
          if rx['return']>0: return rx
          table=rx['table']

    if len(table)==0:
       return {'return':1, 'error':'no points found'}

    # Check if out to module
    pp=''
    if otf_duoa!='':
       if otf_muoa=='': otf_muoa=work['self_module_uid']
       # Try to update this entry to be sure that we can record there, and get path
       ii={'action':'update',
           'module_uoa':otf_muoa,
           'repo_uoa':otf_ruoa,
           'data_uoa':otf_duoa,
           'ignore_update':'yes'}
       rx=ck.access(ii)
       if rx['return']>0: return rx
       pp=rx['path']

    # Save table to file, if needed
    if stjf!='':
       if pp!='':
          ppx=os.path.join(pp, stjf)
       else:
          ppx=stjf

       rx=ck.save_json_to_file({'json_file':ppx, 'dict':table})
       if rx['return']>0: return rx

    # Prepare libraries
    pt=i.get('plot_type','')
    if pt.startswith('mpl_'):

   #    import numpy as np
       import matplotlib as mpl


       if ck.cfg.get('use_internal_engine_for_plotting','')=='yes':
          mpl.use('agg') # if XWindows is not installed, use internal engine
       elif os.environ.get('CK_MPL_BACKEND','')!='':
          mpl.use(os.environ['CK_MPL_BACKEND'])

       import matplotlib.pyplot as plt

       # Set font
       font=i.get('font',{})
       if len(font)==0:
          font = {'family':'arial', 
                  'weight':'normal', 
                  'size': 10}

       plt.rc('font', **font)

       # Configure graph
       gs=cfg['mpl_point_styles']

       sizex=i.get('mpl_image_size_x','')
       if sizex=='': sizex='9'

       sizey=i.get('mpl_image_size_y','')
       if sizey=='': sizey='5'

       dpi=i.get('mpl_image_dpi','')
       if dpi=='': dpi='100'

       if sizex!='' and sizey!='' and dpi!='':
          fig=plt.figure(figsize=(int(sizex),int(sizey)))
       else:
          fig=plt.figure()

       if i.get('plot_grid','')=='yes':
          plt.grid(True)

       bl=i.get('bound_lines','')

       if pt=='mpl_3d_scatter' or pt=='mpl_3d_trisurf':
          from mpl_toolkits.mplot3d import Axes3D
          sp=fig.add_subplot(111, projection='3d')
       else:
          sp=fig.add_subplot(111)

       if i.get('xscale_log','')=='yes': sp.set_xscale('log')
       if i.get('yscale_log','')=='yes': sp.set_yscale('log')
       if i.get('zscale_log','')=='yes': sp.set_zscale('log')

       # Find min/max in all data and all dimensions
       tmin=[]
       tmax=[]

       for g in table:
           gt=table[g]
           for k in gt:
               for d in range(0, len(k)):
                   v=k[d]
                   if len(tmin)<=d:
                      tmin.append(v)
                      tmax.append(v)
                   else:
                      if v<tmin[d]: tmin[d]=v
                      if v>tmax[d]: tmax[d]=v 
                              
       # If density or heatmap, find min and max for both graphs:
       if pt=='mpl_1d_density' or pt=='mpl_1d_histogram' or pt=='mpl_2d_heatmap' or pt=='mpl_3d_scatter' or pt=='mpl_3d_trisurf':
          index=0
          if pt=='mpl_2d_heatmap': index=2

          dmean=0.0
          start=True
          dmin=0.0
          dmax=0.0
          it=0
          dt=0
          for g in table:
              gt=table[g]

              for k in gt:
                  v=k[index]

                  if v!=None and v!='':
                     if start: 
                        dmin=v
                        start=False
                     else: 
                        dmin=min(dmin, v)

                     if start: 
                        dmax=v
                        start=False
                     else: 
                        dmax=max(dmax, v)

                     it+=1
                     dt+=v

          if it!=0: dmean=dt/it

       # If heatmap, prepare colorbar
       if pt=='mpl_2d_heatmap' or pt=='mpl_3d_trisurf':
          from matplotlib import cm
          xcmap = plt.cm.get_cmap('coolwarm')


       xmin=i.get('xmin','')
       xmax=i.get('xmax','')
       ymin=i.get('ymin','')
       ymax=i.get('ymax','')

       if xmin!='':
          sp.set_xlim(left=float(xmin))
       if xmax!='':
          sp.set_xlim(right=float(xmax))
       if ymin!='':
          sp.set_ylim(bottom=float(ymin))
       if ymax!='':
          sp.set_ylim(top=float(ymax))

       xerr=i.get('display_x_error_bar','')
       yerr=i.get('display_y_error_bar','')
       zerr=i.get('display_z_error_bar','')

       if pt=='mpl_2d_bars' or pt=='mpl_2d_lines':
          ind=[]
          gt=table['0']
          xt=0
          for q in gt:

              xt+=1

              if xt==xtp: 
                 v=q[0]
                 xt=0
              else: 
                 v=0

              ind.append(v)

          sp.set_xticks(ind)
          sp.set_xticklabels(ind, rotation=-20)

          width=0.9/len(table)

       # Iterate over separate graphs and add points
       s=0

       for g in sorted(table, key=int):
           gt=table[g]

           lbl=''
           if s<len(lsg): lbl=lsg[s]

           xpst=pst.get(g,{})

           elw=int(xpst.get('elinewidth',0))

           cl=xpst.get('color','')
           if cl=='': cl=gs[s]['color']

           sz=xpst.get('size','')
           if sz=='': sz=gs[s]['size']

           mrk=xpst.get('marker','')
           if mrk=='': mrk=gs[s]['marker']

           lst=xpst.get('line_style','')
           if lst=='': lst=gs[s].get('line_style', '-')

           heatmap=None

           if pt=='mpl_2d_scatter' or pt=='mpl_2d_bars' or pt=='mpl_2d_lines':
              mx=[]
              mxerr=[]
              my=[]
              myerr=[]

              for u in gt:
                  iu=0

                  # Check if no None
                  partial=False
                  for q in u:
                      if q==None:
                         partial=True
                         break

                  if not partial:
                     mx.append(u[iu])
                     iu+=1

                     if xerr=='yes':
                        mxerr.append(u[iu])
                        iu+=1 

                     my.append(u[iu])
                     iu+=1

                     if yerr=='yes':
                        myerr.append(u[iu])
                        iu+=1 

              if pt=='mpl_2d_bars':
                 mx1=[]
                 for q in mx:
                     mx1.append(q+width*s)

                 if yerr=='yes':
                    sp.bar(mx1, my, width=width, edgecolor=cl, facecolor=cl, align='center', yerr=myerr, label=lbl) # , error_kw=dict(lw=2))
                 else:
                    sp.bar(mx1, my, width=width, edgecolor=cl, facecolor=cl, align='center', label=lbl)

              elif pt=='mpl_2d_lines':

                 if yerr=='yes':
                     sp.errorbar(mx, my, yerr=myerr, ls='none', c=cl, elinewidth=elw)
                 sp.plot(mx, my, c=cl, label=lbl)


              else:
                 if xerr=='yes' and yerr=='yes':
                    sp.errorbar(mx, my, xerr=mxerr, yerr=myerr, ls='none', c=cl, elinewidth=elw, label=lbl)
                 elif xerr=='yes' and yerr!='yes':
                    sp.errorbar(mx, my, xerr=mxerr, ls='none',  c=cl, elinewidth=elw, label=lbl)
                 elif yerr=='yes' and xerr!='yes':
                     sp.errorbar(mx, my, yerr=myerr, ls='none', c=cl, elinewidth=elw, label=lbl)
                 else:
                    sp.scatter(mx, my, s=int(sz), edgecolor=cl, c=cl, marker=mrk, label=lbl)

                 if xpst.get('frontier','')=='yes':
                    # not optimal solution, but should work (need to sort to draw proper frontier)
                    a=[]
                    for q in range(0, len(mx)):
                        a.append([mx[q],my[q]])

                    b=sorted(a, key=lambda k: k[0])

                    mx=[tmin[0]]
                    my=[tmax[1]]

                    for j in b:
                        mx.append(j[0])
                        my.append(j[1])

                    mx.append(tmax[0])
                    my.append(tmin[1])

                    sp.plot(mx, my, c=cl, linestyle=lst, label=lbl)

           elif pt=='mpl_1d_density' or pt=='mpl_1d_histogram':
              if not start: # I.e. we got non empty points
                 xbins=i.get('bins', 100)

                 mx=[]
                 for u in gt:
                     mx.append(u[0])

                 ii={'action':'analyze',
                     'min':dmin,
                     'max':dmax,
                     'module_uoa':cfg['module_deps']['math.variation'],
                     'bins':xbins,
                     'characteristics_table':mx}

                 r=ck.access(ii)
                 if r['return']>0: return r

                 xs=r['xlist']
                 dxs=r['ylist']

                 pxs=r['xlist2s']
                 dpxs=r['ylist2s']

                 if pt=='mpl_1d_density':
                    sp.plot(xs,dxs, label=lbl)
                    sp.plot(pxs, dpxs, 'x', mec='r', mew=2, ms=8) #, mfc=None, mec='r', mew=2, ms=8)
                    sp.plot([dmean,dmean],[0,dpxs[0]],'g--',lw=2)
                 else:
                    plt.hist(mx, bins=xbins, normed=True, label=lbl)

           elif pt=='mpl_2d_heatmap' or pt=='mpl_3d_scatter' or pt=='mpl_3d_trisurf':
                mx=[]
                mxerr=[]
                my=[]
                myerr=[]
                mz=[]
                mzerr=[]

                for u in gt:
                    iu=0

                    # Check if no None
                    partial=False
                    for q in u:
                        if q==None:
                           partial=True
                           break

                    if not partial:
                       mx.append(u[iu])
                       iu+=1
                       if xerr=='yes':
                          mxerr.append(u[iu])
                          iu+=1 

                       my.append(u[iu])
                       iu+=1
                       if yerr=='yes':
                          myerr.append(u[iu])
                          iu+=1 

                       mz.append(u[iu])
                       iu+=1
                       if zerr=='yes':
                          mzerr.append(u[iu])
                          iu+=1 

                if pt=='mpl_2d_heatmap':
                   heatmap=sp.scatter(mx, my, c=mz, s=int(sz), marker=mrk, lw=elw, vmin=dmin, vmax=dmax, cmap=xcmap)
                elif pt=='mpl_3d_scatter':
                   heatmap=sp.scatter(mx,my,mz, c=cl, s=int(sz), marker=mrk, lw=elw)
                elif pt=='mpl_3d_trisurf':
                   heatmap=sp.plot_trisurf(mx,my,mz,cmap=cm.coolwarm, lw=elw)
           s+=1
           if s>=len(gs):s=0

       # If heatmap, finish colors
       if pt=='mpl_2d_heatmap' or pt=='mpl_3d_trisurf':
          plt.colorbar(heatmap, orientation=xpst.get('colorbar_orietation','horizontal'), label=xpst.get('colorbar_label',''))

       # If bounds
       if bl=='yes':
          xbs=i.get('bound_style',':')
          xbc=i.get('bound_color','r')
          sp.plot([tmin[0],tmax[0]],[tmin[1],tmin[1]], linestyle=xbs, c=xbc)
          sp.plot([tmin[0],tmin[0]],[tmin[1],tmax[1]], linestyle=xbs, c=xbc)

       # Set axes names
       axd=i.get('axis_x_desc','')
       if axd!='': plt.xlabel(axd)

       ayd=i.get('axis_y_desc','')
       if ayd!='': plt.ylabel(ayd)

       atitle=i.get('title','')
       if atitle!='': plt.title(atitle)

#       handles, labels = plt.get_legend_handles_labels()
       plt.legend() #handles, labels)

       if otf=='':
          plt.show()
       else:
          if pp!='':
             ppx=os.path.join(pp, otf)
          else:
             ppx=otf

          plt.savefig(ppx)

    else:
       return {'return':1, 'error':'this type of plot ('+pt+') is not supported'}

    return {'return':0}

##############################################################################
# Continuously updated plot

def continuous_plot(i):
    """
    Input:  {

            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    for q in range(0, 1000):
        r=plot(i)
        if r['return']>0: return r

        x=ck.inp({'text':'Press any key'})

    return {'return':0}

##############################################################################
# view entry as html

##############################################################################
# view entry as html

def html_viewer(i):
    """
    Input:  {
              data_uoa

              url_base
              url_pull

              url_pull_tmp
              tmp_data_uoa

              form_name     - current form name

              (all_params)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    import os

    h=''
    raw='no'
    top='no'

    duoa=i['data_uoa']
    burl=i['url_base']
    purl=i['url_pull']

    tpurl=i['url_pull_tmp']
    tpuoa=i['tmp_data_uoa']

    ap=i.get('all_params',{})

    ruoa=ap.get('ck_top_repo','')
    muoa=ap.get('ck_top_module','')

    cparams=ap.get('graph_params','') # current graph params

    itype='png'

    # Check autorefresh
    ar=ap.get(var_post_autorefresh,'')
    if ar=='on':
       ap[var_post_refresh_graph]='yes'

    form_name=i['form_name']
    form_submit='document.'+form_name+'.submit();'

    art=ap.get(var_post_autorefresh_time,'')
    iart=5
    if art!='':
       try:
          iart=int(art)
       except ValueError:
          iart=5

    if ar=='on':
       h+='\n'
       h+='<script language="javascript">\n'
       h+=' <!--\n'
       h+='  setTimeout(\''+form_submit+'\','+str(iart*1000)+');\n'
       h+=' //-->\n'
       h+='</script>\n'
       h+='\n'

       # Set replotting
       jj={'action':'create_input',
           'module_uoa':cfg['module_deps']['wfe'],
           'type':'hidden', 
           'name': var_post_refresh_graph, 
           'value':'yes'}
       rx=ck.access(jj)
       if rx['return']>0: return rx
       h+=rx['html']+'\n'

    if duoa!='':
       # Load entry
       rx=ck.access({'action':'load',
                     'module_uoa':work['self_module_uid'],
                     'data_uoa':duoa})
       if rx['return']>0: return rx

       pp=rx['path']

       dd=rx['dict']
       duid=rx['data_uid']

       name=dd.get('name','')

       h+=' <span id="ck_entries1a">'+name+'</span><br>\n'
       h+=' <div id="ck_entries_space4"></div>\n'

       graphs=dd.get('graphs',[])

       # If more than one subgraph, prepare selector
       hsb=''

       igraph=0
       cgraph=0
       x=ap.get(var_post_cur_subgraph,'')
       try:
          cgraph=int(x)
       except ValueError:
          cgraph=0

       sgraph=ap.get(var_post_subgraph,'')

       if len(graphs)>1:
          dx=[]
          jgraph=0
          for q in graphs:
              vid=q.get('id','')
              if vid==sgraph: 
                 igraph=jgraph
              dx.append({'name':q.get('name',''), 'value':vid})
              jgraph+=1

          jj={'action':'create_selector',
              'module_uoa':cfg['module_deps']['wfe'],
              'name': var_post_subgraph, 
              'onchange':form_submit,
              'data':dx,
              'selected_value':sgraph}

          rx=ck.access(jj)
          if rx['return']>0: return rx
          hsb=rx['html']+'\n'

          if igraph!=cgraph:
             ap[var_post_reset_graph]='yes'
             cgraph=igraph

          # Save current subgraph to detect change and reset ...
          jj={'action':'create_input',
              'module_uoa':cfg['module_deps']['wfe'],
              'type':'hidden', 
              'name': var_post_cur_subgraph, 
              'value':str(cgraph)}
          rx=ck.access(jj)
          if rx['return']>0: return rx
          h+=rx['html']+'\n'

       # Visualize
       if igraph<len(graphs):
          g=graphs[igraph]

          gid=g.get('id','')
          if gid!='':
             # Get graph params
             if g.get('notes','')!='':
                h+='<i>'+g['notes']+'</i>'
                h+=' <hr class="ck_hr">\n'

             if hsb!='':
                h+='<center>Select subgraph:&nbsp;'+hsb+'</center>\n'
                h+=' <hr class="ck_hr">\n'

             image=gid+'.'+itype

             params=g.get('params',{})

             problem_converting_json=''

             if var_post_reset_graph not in ap and cparams!='':
                rx=ck.convert_json_str_to_dict({'str':cparams, 'skip_quote_replacement':'yes'})
                if rx['return']>0:
                   problem_converting_json=rx['error']
                else:
                   params=rx['dict']

             rx=ck.dumps_json({'dict':params, 'sort_keys':'yes'})
             if rx['return']>0: return rx
             jparams=rx['string']

             # Check if need to regenerate
             problem=''
             if var_post_refresh_graph in ap:
                import copy

                ii=copy.deepcopy(params)
                ii['action']='plot'
                ii['module_uoa']=work['self_module_uoa']

                image=ap.get(var_post_tmp_graph_file,'')
                if image=='':
                   rx=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.'+itype, 'remove_dir':'yes'})
                   if rx['return']>0: return rx
                   image=rx['file_name']

                ii['out_to_file']=image

                # Preset current entry params
                jj={'action':'create_input',
                    'module_uoa':cfg['module_deps']['wfe'],
                    'type':'hidden', 
                    'name': var_post_tmp_graph_file, 
                    'value':image}
                rx=ck.access(jj)
                if rx['return']>0: return rx
                h+=rx['html']+'\n'

                if ck.cfg.get('graph_tmp_repo_uoa','')!='':
                   ii['out_repo_uoa']=ck.cfg['graph_tmp_repo_uoa']

                ii['out_module_uoa']='tmp'
                ii['out_data_uoa']=tpuoa

#               (save_table_to_json_file)             - save table to json file

                rx=ck.access(ii)
                if rx['return']>0: 
                   problem=rx['error']

                purl=tpurl

             # Prepare html

             size_x=params.get('size_x','')
             size_y=params.get('size_y','')

             h+=' <table border="0" cellpadding="3" width="100%">\n'
             h+=' <tr>\n'

             extra=''
             if size_x!='': extra+='width="'+str(size_x)+'" '

             h+='  <td valign="top" '+extra+'>\n'
             h+='<b><small>Graph:</small></b>\n'
             if problem!='':
                h+='<br><br><span style="color:red;"><i>Problem: '+problem+'!</i></span><br>\n'
             else:
                if image!='':
                   if size_y!='': extra+='height="'+str(size_y)+'" '
                   h+='   <img src="'+purl+image+'" '+extra+'>'
             h+='  </td>\n'

             h+='  <td valign="top">\n'

             x='width:100%;'
             if size_y!='': x+='height:'+str(size_y)+'px;'

             h+='<b><small>Graph params (for reproducibility):</small></b>\n'

             if problem_converting_json!='':
                h+='<br><br><span style="color:red;"><i>'+problem_converting_json+'</i></span><br>\n'
                    
             h+='   <textarea name="graph_params" style="'+x+'">\n'
             h+=jparams+'\n'
             h+='   </textarea><br>\n'

             h+='  </td>\n'

             h+=' </tr>\n'
             h+='</table>\n'

             h+=' <hr class="ck_hr">\n'

             h+='<center>\n'
             h+='<button type="submit" name="'+var_post_refresh_graph+'">Replot graph</button>\n'
             h+='<button type="submit" name="'+var_post_reset_graph+'">Reset graph</button>\n'

             checked=''
             if ar=='on': checked=' checked '
             h+='&nbsp;&nbsp;&nbsp;Auto-replot graph:&nbsp;<input type="checkbox" name="'+var_post_autorefresh+'" id="'+var_post_autorefresh+'" onchange="submit()"'+checked+'>,'
             h+='&nbsp;seconds: <input type="text" name="'+var_post_autorefresh_time+'" value="'+str(iart)+'">\n'
             h+='</center>\n'

    return {'return':0, 'raw':raw, 'show_top':top, 'html':h}