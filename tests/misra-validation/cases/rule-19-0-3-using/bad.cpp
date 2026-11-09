// Seeded violation: an #include after a using-declaration.
#include <cstddef>

using std::size_t;

#include <cstdint>

namespace kv::rule_19_0_3_using::bad {

constexpr size_t kCount = 2U;
constexpr std::uint8_t kValue = 1U;

}  // namespace kv::rule_19_0_3_using::bad
