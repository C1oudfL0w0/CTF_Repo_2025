#![windows_subsystem = "windows"]
static FONT_DATA: &[u8] = include_bytes!("../VN Font.ttf");
use minifb::{Window, WindowOptions};
use rusttype::{Font, Scale};
fn main() {
    // 创建一个窗口
    let mut window = Window::new(
        "VN_lang:It's Your FLAG!!!!!",
        800,
        600,
        WindowOptions::default(),
    )
    .unwrap();

    // // 读取并加载字体文件
    // let mut font_data = Vec::new();
    // File::open("VN Font.ttf")
    //     .unwrap()
    //     .read_to_end(&mut font_data)
    //     .unwrap();
    let font = Font::try_from_bytes(FONT_DATA).unwrap();

    // 设置文本渲染的参数
    let scale = Scale { x: 48.0, y: 48.0 }; // 字体大小
    let color = (255, 255, 255, 255); // 白色

    // 创建一个空的缓冲区用于绘制
    let mut buffer: Vec<u32> = vec![0; 800 * 600];

    // 渲染文本
    // Fake Flag lol
    let text1 = "VNCTF{VNCTF";
    let text2 = "VNCTFVNCTF";
    let text3 = "CTFVNCTFVN";
    let text4 = "VNFTCVNFTC";
    let text5 = "CTFVNCTFVN}";
    let (width, height) = window.get_size();

    // 渲染文本到缓冲区
    let layout1 = font.layout(text1, scale, rusttype::point(10.0, 50.0));
    let layout2 = font.layout(text2, scale, rusttype::point(10.0, 100.0));
    let layout3 = font.layout(text3, scale, rusttype::point(10.0, 150.0));
    let layout4 = font.layout(text4, scale, rusttype::point(10.0, 200.0));
    let layout5 = font.layout(text5, scale, rusttype::point(10.0, 250.0));

    for glyph in layout1 {
        if let Some(bb) = glyph.pixel_bounding_box() {
            glyph.draw(|x, y, v| {
                // 计算绝对坐标
                let x = (x as i32 + bb.min.x).max(0) as usize;
                let y = (y as i32 + bb.min.y).max(0) as usize;

                // 边界检查
                if x < width && y < height {
                    // 计算缓冲区位置
                    let idx = y * width + x;

                    if v > 0.5 {
                        let pixel =
                            ((color.0 as u32) << 16) | ((color.1 as u32) << 8) | (color.2 as u32);
                        buffer[idx] = pixel;
                    }
                }
            });
        }
    }
    for glyph in layout2 {
        if let Some(bb) = glyph.pixel_bounding_box() {
            glyph.draw(|x, y, v| {
                // 计算绝对坐标
                let x = (x as i32 + bb.min.x).max(0) as usize;
                let y = (y as i32 + bb.min.y).max(0) as usize;

                // 边界检查
                if x < width && y < height {
                    // 计算缓冲区位置
                    let idx = y * width + x;

                    if v > 0.5 {
                        let pixel =
                            ((color.0 as u32) << 16) | ((color.1 as u32) << 8) | (color.2 as u32);
                        buffer[idx] = pixel;
                    }
                }
            });
        }
    }
    for glyph in layout3 {
        if let Some(bb) = glyph.pixel_bounding_box() {
            glyph.draw(|x, y, v| {
                // 计算绝对坐标
                let x = (x as i32 + bb.min.x).max(0) as usize;
                let y = (y as i32 + bb.min.y).max(0) as usize;

                // 边界检查
                if x < width && y < height {
                    // 计算缓冲区位置
                    let idx = y * width + x;

                    if v > 0.5 {
                        let pixel =
                            ((color.0 as u32) << 16) | ((color.1 as u32) << 8) | (color.2 as u32);
                        buffer[idx] = pixel;
                    }
                }
            });
        }
    }
    for glyph in layout4 {
        if let Some(bb) = glyph.pixel_bounding_box() {
            glyph.draw(|x, y, v| {
                // 计算绝对坐标
                let x = (x as i32 + bb.min.x).max(0) as usize;
                let y = (y as i32 + bb.min.y).max(0) as usize;

                // 边界检查
                if x < width && y < height {
                    // 计算缓冲区位置
                    let idx = y * width + x;

                    if v > 0.5 {
                        let pixel =
                            ((color.0 as u32) << 16) | ((color.1 as u32) << 8) | (color.2 as u32);
                        buffer[idx] = pixel;
                    }
                }
            });
        }
    }
    for glyph in layout5 {
        if let Some(bb) = glyph.pixel_bounding_box() {
            glyph.draw(|x, y, v| {
                // 计算绝对坐标
                let x = (x as i32 + bb.min.x).max(0) as usize;
                let y = (y as i32 + bb.min.y).max(0) as usize;

                // 边界检查
                if x < width && y < height {
                    // 计算缓冲区位置
                    let idx = y * width + x;

                    if v > 0.5 {
                        let pixel =
                            ((color.0 as u32) << 16) | ((color.1 as u32) << 8) | (color.2 as u32);
                        buffer[idx] = pixel;
                    }
                }
            });
        }
    }

    // 渲染缓冲区到窗口
    while window.is_open() {
        window.update_with_buffer(&buffer, width, height).unwrap();
    }
}
