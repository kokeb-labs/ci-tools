// Seeded violation: an #include after a declaration.
namespace kv::rule_19_0_3::bad {

constexpr int kEarly = 1;

}  // namespace kv::rule_19_0_3::bad

#include <cstdint>  // seeded

namespace kv::rule_19_0_3::bad {

constexpr std::uint8_t kLate = 2U;

}  // namespace kv::rule_19_0_3::bad
