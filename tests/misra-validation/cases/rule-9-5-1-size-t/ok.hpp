// Compliant legacy for statements the pack misreports (Rule 9.5.1).
#ifndef KV_RULE_9_5_1_OK_SIZE_T_HPP
#define KV_RULE_9_5_1_OK_SIZE_T_HPP

#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_9_5_1::size_t_counter {

inline constexpr std::size_t kCount = 4U;

constexpr std::size_t Half(std::size_t n) noexcept { return n / 2U; }

// A std::size_t counter against a constant bound: std::size_t is an unsigned integer type.
inline std::uint32_t SumConst(const std::array<std::uint32_t, kCount>& a) noexcept {
  std::uint32_t s = 0U;
  for (std::size_t i = 0U; i < kCount; ++i) {
    s += a[i];
  }
  return s;
}

// Inside a class template: std::array::size() and a constexpr call with constant arguments are
// constant expressions.
template <typename T>
class Table {
 public:
  [[nodiscard]] std::uint32_t Sum() const noexcept {
    std::uint32_t s = 0U;
    for (std::size_t i = 0U; i < cells_.size(); ++i) {
      s += cells_[i];
    }
    return s;
  }
  [[nodiscard]] std::uint32_t SumHalf() const noexcept {
    std::uint32_t s = 0U;
    for (std::uint32_t i = 0U; i < static_cast<std::uint32_t>(Half(kCount)); ++i) {
      s += cells_[i];
    }
    return s;
  }

 private:
  std::array<std::uint32_t, kCount> cells_{};
};

inline std::uint32_t Use() noexcept {
  const Table<int> t{};
  const std::array<std::uint32_t, kCount> a{};
  return SumConst(a) + t.Sum() + t.SumHalf();
}

}  // namespace kv::rule_9_5_1::size_t_counter

#endif  // KV_RULE_9_5_1_OK_SIZE_T_HPP
