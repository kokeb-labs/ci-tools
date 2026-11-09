// Seeded violation: puts, a FILE pointer and EOF through <stdio.h>, unqualified.
#include <stdio.h>

namespace kv::rule_30_0_1::bad_c_header {

int emit(FILE* out, const char* text) {
  if (fputs(text, out) == EOF) {
    return EOF;
  }
  return ::puts(text);
}

}  // namespace kv::rule_30_0_1::bad_c_header
