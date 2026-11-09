// Compliant near miss: a class-specific (member) operator delete in the unsized form only. Rule 21.6.4 is about
// the global operator delete, so a member form without its sized partner is outside it.
#ifndef KV_RULE_21_6_4_OK_CLASS_SPECIFIC_HPP
#define KV_RULE_21_6_4_OK_CLASS_SPECIFIC_HPP

#include <array>
#include <cstddef>
#include <cstdint>

namespace kv::rule_21_6_4::ok_class_specific {

struct Block {
  static void* operator new(std::size_t size);
  static void operator delete(void* block) noexcept;
  std::array<std::uint32_t, 4U> words;
};

[[nodiscard]] inline std::uint32_t first_word(const Block& block) { return block.words[0]; }

}  // namespace kv::rule_21_6_4::ok_class_specific

#endif  // KV_RULE_21_6_4_OK_CLASS_SPECIFIC_HPP
