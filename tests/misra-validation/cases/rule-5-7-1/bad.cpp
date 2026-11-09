// Seeded violation: a block comment opened inside a block comment.
#include <cstdint>

namespace kv::rule_5_7_1::bad {

/* outer comment /* opens another one inside */  // seeded
std::uint32_t one() { return 1U; }

}  // namespace kv::rule_5_7_1::bad
