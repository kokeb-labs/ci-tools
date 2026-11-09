// Seeded violation: strcmp called unqualified through a using-declaration.
#include <cstring>

namespace kv::rule_21_2_2::bad_using {

using std::strcmp;

bool same(const char* a, const char* b) { return strcmp(a, b) == 0; }  // seeded

}  // namespace kv::rule_21_2_2::bad_using
