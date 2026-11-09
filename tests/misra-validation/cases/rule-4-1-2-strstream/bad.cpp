// Seeded violation: the deprecated strstream classes.
#include <strstream>

namespace kv::rule_4_1_2_strstream::bad {

bool good(std::istrstream& s) { return s.good(); }  // seeded

}  // namespace kv::rule_4_1_2_strstream::bad
