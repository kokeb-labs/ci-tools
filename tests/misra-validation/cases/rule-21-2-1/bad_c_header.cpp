// Seeded violation: atol and atoll reached through the C header, unqualified.
#include <stdlib.h>

namespace kv::rule_21_2_1::bad_c_header {

long parse_long(const char* text) { return ::atol(text); }  // seeded

long long parse_long_long(const char* text) { return atoll(text); }  // seeded

}  // namespace kv::rule_21_2_1::bad_c_header
