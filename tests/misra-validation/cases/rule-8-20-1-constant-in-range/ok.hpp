// Compliant: unsigned arithmetic on constant expressions that stays in range (a static_assert operand
// and a requires-clause over template parameters).
#ifndef KV_RULE_8_20_1_CONSTANT_IN_RANGE_OK_HPP
#define KV_RULE_8_20_1_CONSTANT_IN_RANGE_OK_HPP

#include <cstddef>
#include <cstdint>

namespace kv::rule_8_20_1_constant_in_range::ok {

enum class Index : std::uint8_t { kFirst = 0U, kSecond = 1U, kLast = 2U };

constexpr std::size_t at(Index i) noexcept { return static_cast<std::size_t>(i); }

inline constexpr std::size_t kCount = 3U;

static_assert((at(Index::kLast) + 1U) == kCount);

template <std::uint32_t Shift, std::uint32_t Width>
  requires(Width > 0U) && ((Shift + Width) <= 8U)
struct Field {
  static constexpr std::uint32_t kMask = ((1U << Width) - 1U) << Shift;
};

inline constexpr std::uint32_t kProtectMask = Field<2U, 2U>::kMask;

}  // namespace kv::rule_8_20_1_constant_in_range::ok

#endif  // KV_RULE_8_20_1_CONSTANT_IN_RANGE_OK_HPP
