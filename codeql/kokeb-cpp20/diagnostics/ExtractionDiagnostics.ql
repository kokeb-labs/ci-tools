/**
 * @id kokeb/diagnostics/extraction-diagnostics
 * @name Extractor errors
 * @description Errors the CodeQL front end reported while extracting the build (severity 3 discretionary error,
 *              4 error, 5 catastrophe): code it may not have modelled, for ru-misra's extraction-coverage check.
 * @kind table
 */

import cpp

from Diagnostic d, string file, int line
where
  d.getSeverity() >= 3 and
  (
    file = d.getFile().getRelativePath() and line = d.getLocation().getStartLine()
    or
    not exists(d.getFile().getRelativePath()) and file = "" and line = 0
  )
select file, line, d.getSeverity(), d.getMessage()
