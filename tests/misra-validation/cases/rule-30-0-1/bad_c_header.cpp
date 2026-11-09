// Seeded violation: puts, a FILE pointer and EOF through <stdio.h>, unqualified.
#include <stdio.h>

namespace kv::rule_30_0_1::bad_c_header {

int emit(FILE* out, const char* text) {  // seeded: codeql
  if (fputs(text, out) == EOF) {  // seeded
    return EOF;  // seeded: codeql
  }
  return ::puts(text);  // seeded
}

}  // namespace kv::rule_30_0_1::bad_c_header
