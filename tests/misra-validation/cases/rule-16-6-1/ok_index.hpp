// Near miss: member operator[] is not a symmetric binary operator.
#ifndef KV_RULE_16_6_1_OK_INDEX_HPP
#define KV_RULE_16_6_1_OK_INDEX_HPP

#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_16_6_1::ok_index {

class Table {
 public:
  [[nodiscard]] std::uint8_t operator[](std::size_t i) const { return data_.at(i); }

 private:
  std::array<std::uint8_t, 4> data_{};
};

}  // namespace kv::rule_16_6_1::ok_index

#endif  // KV_RULE_16_6_1_OK_INDEX_HPP
