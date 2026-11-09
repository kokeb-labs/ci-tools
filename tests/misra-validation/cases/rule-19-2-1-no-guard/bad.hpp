// Seeded violation: a header without an include guard.  // seeded
#include <cstdint>

namespace kv::rule_19_2_1_no_guard::bad {

inline std::uint8_t one() { return 1U; }

}  // namespace kv::rule_19_2_1_no_guard::bad
