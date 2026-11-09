// Seeded violation: isalpha and tolower through <ctype.h>, unqualified and ::-qualified.
#include <ctype.h>

namespace kv::rule_24_5_1::bad_c_header {

bool letter(int c) { return isalpha(c) != 0; }

int lower(int c) { return ::tolower(c); }

}  // namespace kv::rule_24_5_1::bad_c_header
