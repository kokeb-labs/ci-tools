/**
 * @id kokeb/diagnostics/compiled-files
 * @name Files in the database
 * @description Every translation unit the traced build compiled (unit = true) and every file extracted with it,
 *              for ru-misra's extraction-coverage check.
 * @kind table
 */

import cpp

from File f, boolean unit
where
  exists(f.getRelativePath()) and
  if exists(Compilation c | c.getAFileCompiled() = f) then unit = true else unit = false
select f.getAbsolutePath(), f.getRelativePath(), unit
