#!/usr/bin/python
import copy
import time
import yaml
import os, re
import sys
import errno

from kickstart import kickstart

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

class KSWriter():
    def __init__(self, configs=None, repos=None, outdir=".", config=None, packages=False):
        self.image_filename = configs
        self.repo_filename = repos
        self.outdir = outdir
        self.packages = packages
        self.config = config
        self.image_stream = file(self.image_filename, 'r')
        self.repo_stream = file(self.repo_filename, 'r')
        self.extra = {}
        self.repo_meta = yaml.load(self.repo_stream)
        self.image_meta = yaml.load(self.image_stream)

    def merge(*input):
        return list(reduce(set.union, input, set()))

    def dump(self):
        print yaml.dump(yaml.load(self.stream))

    def parse(self, img):
        conf = copy.copy(self.image_meta['Default'])
        plat = copy.copy(self.image_meta[img['Platform']])
        conf.update(plat)
        conf.update(img)
        lval = ['Repos', 'Groups', 'PostScripts', 'NoChrootScripts', 'RemovePackages', 'ExtraPackages']
        lvald = {}
        for l in lval:
            full = []
            if self.image_meta['Default'].has_key(l) and self.image_meta['Default'][l]:
                full = full + self.image_meta['Default'][l]
            if plat.has_key(l) and plat[l]:
                full = full + plat[l]
            if img.has_key(l) and img[l]:
                full = full + img[l]
            lvald[l] = sorted(set(full), key=full.index)
            #print full
        conf.update(lvald)
        #print conf
        postscript = ""
        for scr in conf['PostScripts']:
            if os.path.exists('./custom/scripts/%s.post' %scr):
                f = open('./custom/scripts/%s.post' %scr, 'r')
                postscript += f.read()
                postscript += "\n"
                f.close()
            else:
                print './custom/scripts/%s.post not found, skipping.' %scr

        nochrootscript = ""
        for scr in conf['NoChrootScripts']:
            if os.path.exists('./custom/scripts/%s.nochroot' %scr):
                f = open('./custom/scripts/%s.nochroot' %scr, 'r')
                nochrootscript += f.read()
                nochrootscript += "\n"
                f.close()
            else:
                print './custom/scripts/%s.nochroot not found, skipping.' %scr

        ptab = ""
        for g in [ plat, img ]:
            if g.has_key("Part"):
                f = open("./custom/part/%s" %g['Part'] )
                ptab = f.read()
                f.close()

        conf['Part'] = ptab
        conf['Post'] = postscript
        conf['NoChroot'] = nochrootscript
        return conf

    def process_files(self,  meta,  repos):
        new_repos = []
        if meta.has_key("Architecture") and  meta['Architecture']:
            for repo in repos:
                r = {}
                r['Name'] = repo['Name']
                if repo.has_key('Options'):
                    r['Options'] = repo['Options']
                r['Url'] = repo['Url'].replace("@ARCH@", meta['Architecture'])
                r['Url'] = r['Url'].replace("@RELEASE@", meta['Baseline'])
                new_repos.append(r)
        else:
            new_repos = repos

        nameSpace = {'metadata': meta,  'repos': new_repos}
        t = kickstart(searchList=[nameSpace])
        a = str(t)
        if meta.has_key('FileName') and meta['FileName']:
            f = None
            if meta.has_key("Baseline"):
                mkdir_p(meta['Baseline'])
                f = open("%s/%s/%s.ks" %( self.outdir, meta['Baseline'],  meta['FileName'] ), 'w')
            else:
                f = open("%s/%s.ks" %( self.outdir, meta['FileName'] ), 'w')
            f.write(a)
            f.close()

    def generate(self):
        out = {}
        r = self.repo_meta['Repositories']
        if self.image_meta.has_key('Configurations'):
            for img in self.image_meta['Configurations']:
                conf = self.parse(img)
                if self.config:
                    if img.has_key('FileName') and self.config == img['FileName']:
                        print "Creating %s (%s.ks)" %(img['Name'], img['FileName'] )
                        self.process_files(conf, r)
                        break
                else:
                    if conf.has_key('Active') and conf['Active'] :
                        print "Creating %s (%s.ks)" %(img['Name'], img['FileName'] )
                        self.process_files(conf, r)
                    else:
                        print "%s is inactive, not generating %s at this time" %(img['Name'], img['FileName'] )
        for path in self.image_meta['ExternalConfigs']:
            for f in os.listdir(path):
                if f.endswith('.yaml'):
                    fp = file('%s/%s' %(path, f), 'r')
                    local = yaml.load(fp)
                    conf = self.parse(local)
                    if self.config:
                        if self.config == conf['FileName']:
                            if self.packages:
                                out['groups'] = conf['Groups']
                                out['packages'] = conf['ExtraPackages']
                            else:
                                print "Creating %s (%s.ks)" %(conf['Name'], conf['FileName'] )
                                self.process_files(conf, r)
                                break
                    else:
                        if conf.has_key('Active') and conf['Active']:
                            print "Creating %s (%s.ks)" %(conf['Name'], conf['FileName'] )
                            self.process_files(conf, r)
                        else:
                            print "%s is inactive, not generate %s this time" %(conf['Name'], conf['FileName'] )
                else:
                    print "WARNING: File '%s' ignored." % (f)
        return out
