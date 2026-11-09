// Seeded violation: strncmp and strtoul through <string.h> and <stdlib.h>, unqualified.
#include <stdlib.h>
#include <string.h>

namespace kv::rule_21_2_2::bad_c_header {

bool same_prefix(const char* a, const char* b) { return strncmp(a, b, 4U) == 0; }  // seeded

unsigned long to_unsigned(const char* text) { return ::strtoul(text, nullptr, 10); }  // seeded

}  // namespace kv::rule_21_2_2::bad_c_header
