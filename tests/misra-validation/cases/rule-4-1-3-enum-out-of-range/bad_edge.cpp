// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_3_enum_out_of_range::bad_edge {

enum Level { kLow, kMid, kHigh };  // values 0..2, range 0..3
Level from_raw() { return static_cast<Level>(9); }  // seeded
Level negative() { return static_cast<Level>(-1); }  // seeded

}  // namespace kv::rule_4_1_3_enum_out_of_range::bad_edge
