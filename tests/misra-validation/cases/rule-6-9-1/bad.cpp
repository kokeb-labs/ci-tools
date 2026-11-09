// Seeded violation: the declaration and the definition spell the same type with different aliases.
#include <cstdint>

namespace kv::rule_6_9_1::bad {

using Millis = std::uint32_t;

Millis elapsed(Millis start);

std::uint32_t elapsed(std::uint32_t start) { return start + 1U; }

}  // namespace kv::rule_6_9_1::bad
