// Edge cases: more C++17-deprecated C++ library headers ([depr.cpp.headers]).
#include <ccomplex>  // seeded
#include <cstdalign>  // seeded

namespace kv::rule_4_1_2_c_headers::bad_edge {

bool both(bool a, bool b) { return a && b; }

}  // namespace kv::rule_4_1_2_c_headers::bad_edge
