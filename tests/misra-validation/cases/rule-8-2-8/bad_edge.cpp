// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_8::bad_edge {

std::int64_t signed_wide(std::uint32_t const* p) { return reinterpret_cast<std::int64_t>(p); }

}  // namespace kv::rule_8_2_8::bad_edge
