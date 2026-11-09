// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_0_2_3::bad_edge {

std::uint32_t block_alias(std::uint32_t v) {
  using Unused = std::uint32_t;  // block-scope alias, never used  // seeded
  return v;
}

namespace {
enum class Orphan : std::uint8_t { kA, kB };  // internal enumeration, never used  // seeded
}  // namespace

}  // namespace kv::rule_0_2_3::bad_edge
