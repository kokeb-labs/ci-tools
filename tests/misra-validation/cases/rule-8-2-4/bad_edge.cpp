// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_2_4::bad_edge {

std::int32_t handler(std::int32_t code) { return code; }

using Wide = std::int64_t (*)(std::int64_t);
using Narrow = std::int32_t (*)(std::int32_t);

Wide retype() { return reinterpret_cast<Wide>(&handler); }  // seeded

Narrow from_object(void* raw) { return reinterpret_cast<Narrow>(raw); }  // seeded

}  // namespace kv::rule_8_2_4::bad_edge
