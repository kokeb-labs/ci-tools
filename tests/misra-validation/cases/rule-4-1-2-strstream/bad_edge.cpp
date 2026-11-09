// Edge cases: more forms of the violation.
#include <strstream>

namespace kv::rule_4_1_2_strstream::bad_edge {

bool empty(std::strstreambuf& b) { return b.pcount() == 0; }
bool done(std::ostrstream& s) { return s.good(); }

}  // namespace kv::rule_4_1_2_strstream::bad_edge
