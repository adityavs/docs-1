#!/usr/bin/python

import sys
import os.path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
import docs_meta
import makecloth.utils as utils
from makecloth import MakefileCloth

m = MakefileCloth()

paths = docs_meta.render_paths('dict')

def pdf_makefile(name, tag):
    name_tagged = '-'.join([name, tag])
    
    generated_latex = '{0}/latex/{1}.tex'.format(paths['branch-output'], name)
    built_tex = '{0}/latex/{1}.tex'.format(paths['branch-output'], name_tagged)
    built_pdf = '{0}/latex/{1}.pdf'.format(paths['branch-output'], name_tagged)
    staged_pdf_branch = '{0}/{1}-{2}.pdf'.format(paths['branch-staging'], name_tagged, docs_meta.get_branch())
    staged_pdf = '{0}/latex/{1}.pdf'.format(paths['branch-staging'], name_tagged)

    m.section_break(name)
    m.target(target=generated_latex,
             dependency='latex')
    m.job('sed $(SED_ARGS_FILE) -e $(LATEX_CORRECTION) -e $(LATEX_CORRECTION) -e $(LATEX_LINK_CORRECTION) ' + generated_latex)
    m.msg('[latex]: fixing $@ TeX from the Sphinx output.')

    m.target(target=built_tex, dependency=generated_latex)
    m.job('$(PYTHONBIN) {0}/copy-if-needed.py -i {1} -o {2} -b pdf'.format(paths['branch-output'], generated_latex, built_tex))
    m.msg('[pdf]: updated "' + built_tex + '" for pdf generation.')

    m.target(target=staged_pdf_branch, dependency=built_pdf)
    m.job('cp {0} {1}'.format(built_pdf, staged_pdf_branch))
    m.msg('[pdf]: migrated ' + staged_pdf)

    m.target(target=staged_pdf, dependency=staged_pdf_branch)
    m.job('{0}/create-link $(notdir {1}) $(notdir {2}) $(dir {2})'.format(paths['tools'], staged_pdf, staged_pdf_branch))
    m.msg('[pdf]: created link for ' + staged_pdf)

    m.comment('adding ' + name + '.pdf to the build dependency.')
    m.append_var('PDF_OUTPUT', staged_pdf)

def build_all_pdfs(pdfs):
    for pdf in pdfs:
        pdf_makefile(pdf['name'], pdf['type'])

    m.newline()
    m.target(target='.PHONY',
             dependency='manual-pdfs')
    m.target(target='manual-pdfs',
             dependency='$(PDF_OUTPUT)')

def main():
    conf_file = utils.get_conf_file(__file__)
    build_all_pdfs(utils.ingest_yaml(conf_file))

    m.write(sys.argv[1])
    print('[meta-build]: built "' + sys.argv[1] + '" to specify pdf builders.')

if __name__ == '__main__':
    main()
