// Seeded violation: a deprecated C compatibility header.
#include <cstdbool>  // seeded
#include <cstdint>

namespace kv::rule_4_1_2_c_headers::bad {

bool flag(std::uint32_t v) { return v != 0U; }

}  // namespace kv::rule_4_1_2_c_headers::bad
