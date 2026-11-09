// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_20_1::bad_edge {

std::uint32_t below_zero() { return 0U - 1U; }

std::uint32_t product() { return 0x10000U * 0x10000U; }

constexpr std::uint32_t kTop = 0xFFFFFFFFU;
constexpr std::uint32_t kStep = 1U;

std::uint32_t named() { return kTop + kStep; }

}  // namespace kv::rule_8_20_1::bad_edge
