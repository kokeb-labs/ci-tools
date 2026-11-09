// Seeded violation: the deprecated shared_ptr::unique().
#include <memory>
#include <cstdint>

namespace kv::rule_4_1_2_shared_ptr_unique::bad {

bool sole(const std::shared_ptr<std::uint32_t>& p) { return p.unique(); }

}  // namespace kv::rule_4_1_2_shared_ptr_unique::bad
