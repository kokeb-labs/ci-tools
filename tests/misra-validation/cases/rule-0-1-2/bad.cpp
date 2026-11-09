// Seeded violation: a non-void call whose result is neither used nor cast to void.
#include <cstdint>

namespace kv::rule_0_1_2::bad {

std::uint32_t next(std::uint32_t v) { return v + 1U; }

void step(std::uint32_t v) {
  next(v);  // result dropped silently
}

}  // namespace kv::rule_0_1_2::bad
