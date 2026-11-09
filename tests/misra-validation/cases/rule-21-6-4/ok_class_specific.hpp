// Compliant near miss: the global allocation functions are untouched; objects come from a static pool.
#ifndef KV_RULE_21_6_4_OK_CLASS_SPECIFIC_HPP
#define KV_RULE_21_6_4_OK_CLASS_SPECIFIC_HPP

#include <array>
#include <cstdint>

namespace kv::rule_21_6_4::ok_class_specific {

struct Block {
  std::array<std::uint32_t, 4U> words;
};

[[nodiscard]] inline std::uint32_t first_word(const Block& block) { return block.words[0]; }

}  // namespace kv::rule_21_6_4::ok_class_specific

#endif  // KV_RULE_21_6_4_OK_CLASS_SPECIFIC_HPP
