#!/usr/bin/python
# Anas Nashif <anas.nashif@intel.com>
import yaml,  sys

import re, os
from kickstart import kickstart

import copy
import time
import optparse
from time import gmtime, strftime

class KSWriter():
    def __init__(self,  im, rep, out):
        self.image_filename = im
        self.repo_filename = rep
        self.outdir = out
        self.image_stream = file(self.image_filename, 'r')
        self.repo_stream = file(self.repo_filename, 'r')
        self.extra = {}
        pass
    def merge(*input):
        return list(reduce(set.union, input, set()))
        
    def dump(self):
        print yaml.dump(yaml.load(self.stream))
        
        
    def parse(self, img):
        print "Creating %s (%s.ks)" %(img['Name'], img['FileName'] )
        conf = copy.copy(image_meta['Default'])
        plat = copy.copy(image_meta[img['Platform']])
        conf.update(plat)
        conf.update(img)
        lval = ['Repos', 'Groups', 'PostScripts', 'NoChrootScripts', 'RemovePackages', 'ExtraPackages']
        lvald = {}
        for l in lval:
            full = []
            if image_meta['Default'].has_key(l) and image_meta['Default'][l]:
                full = full + image_meta['Default'][l]                
            if plat.has_key(l) and plat[l]:
                full = full + plat[l]
            if img.has_key(l) and img[l]:
                fll = full + img[l]                    
            lvald[l] = set(full)
            #print full
        conf.update(lvald)
        #print conf
        postscript = ""  
        for scr in conf['PostScripts']:
            f = open('./custom/scripts/%s.post' %scr, 'r')
            postscript += f.read()
            postscript += "\n\n"
            f.close()

        nochrootscript = ""              
        for scr in conf['NoChrootScripts']:
            f = open('./custom/scripts/%s.nochroot' %scr, 'r')
            nochrootscript += f.read()
            nochrootscript += "\n\n"
            f.close()

        ptab = ""
        if img.has_key("Part"):
            f = open("./custom/part/%s" %img['Part'] )
            ptab = f.read()
            f.close()  
            
        conf['Part'] = ptab
        conf['Post'] = postscript
        conf['NoChroot'] = nochrootscript
        return conf

    def process_files(self,  meta,  repos):
        new_repos = []
        #print repos
        #print meta
        if meta.has_key("Architecture") and  meta['Architecture']:
            for repo in repos:
                r = {}
                r['Name'] = repo['Name']
                r['Url'] = repo['Url'].replace("@ARCH@", meta['Architecture'])
                new_repos.append(r)
        else:
            new_repos = repos
                
        nameSpace = {'metadata': meta,  'repos': new_repos}
        t = kickstart(searchList=[nameSpace])
        a = str(t)
        if meta.has_key('FileName') and meta['FileName']:
            f = open("%s/%s.ks" %( self.outdir, meta['FileName'] ), 'w')
            f.write(a)
            f.close()

if __name__ == '__main__':
    parser = optparse.OptionParser()

    parser.add_option("-c", "--configs", type="string", dest="configsfile",
                    help="configuration meta file")
    parser.add_option("-o", "--outdir", type="string", dest="outdir",
                    help="outdir")
    parser.add_option("-r", "--repos", type="string", dest="repofile",
                    help="repo meta file")

    (options, args) = parser.parse_args()

    if options.configsfile is None or options.repofile is None:
        print "you need to provide meta files with --configs and --repos"
        sys.exit(1)

    outdir = ""
    if options.outdir is None:
        outdir = "."
    else:
        outdir = options.outdir

    ks = KSWriter(options.configsfile, options.repofile, outdir)
    repo_meta = yaml.load(ks.repo_stream)
    image_meta = yaml.load(ks.image_stream)
    r = repo_meta['Repositories']
    for img in image_meta['Configurations']:
        conf = ks.parse(img)
        ks.process_files(conf, r)
