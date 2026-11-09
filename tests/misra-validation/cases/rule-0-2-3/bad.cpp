// Seeded violation: file-local and block-scope types that nothing uses.
#include <cstdint>

namespace kv::rule_0_2_3::bad {

namespace {
struct Orphan {  // internal linkage, never used  // seeded
  std::uint32_t v;
};
}  // namespace

std::uint32_t local(std::uint32_t v) {
  struct Unused {  // block-scope type, never used  // seeded
    std::uint32_t w;
  };
  return v;
}

}  // namespace kv::rule_0_2_3::bad
