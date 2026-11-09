// Edge cases: more deprecated C compatibility headers.
#include <ciso646>
#include <cstdalign>

namespace kv::rule_4_1_2_c_headers::bad_edge {

bool both(bool a, bool b) { return a and b; }

}  // namespace kv::rule_4_1_2_c_headers::bad_edge
