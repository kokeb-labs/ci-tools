// Edge cases: more forms of the violation.
#include <strstream>

namespace kv::rule_4_1_2_strstream::bad_edge {

bool empty(std::strstreambuf& b) { return b.pcount() == 0; }  // seeded
bool done(std::ostrstream& s) { return s.good(); }  // seeded

}  // namespace kv::rule_4_1_2_strstream::bad_edge
