import argparse
import os
import shutil
import tarfile
import time
from pathlib import Path
from typing import Union
from compression import zstd
import bz2

class ArchiveProcessor:
    
    SUPPORTED_FORMATS = {'.zstd', '.bz2'}
    TEMP_EXTENSION = '.temp.untar'
    
    def __init__(self, benchmark_mode: bool = False):
        self.benchmark_mode = benchmark_mode
    
    def create_archive(self, source: str, output: str) -> bool:
        source_path = Path(source)
        output_path = Path(output)
        
        if not self._validate_source(source_path):
            return False
        
        if not self._validate_output_format(output_path):
            return False
        
        return self._execute_with_benchmark(
            f"создание {output_path.name}",
            lambda: self._compress(source_path, output_path)
        )
    
    def extract_archive(self, archive: str, output: str) -> bool:
        archive_path = Path(archive)
        output_path = Path(output)
        
        if not self._validate_source(archive_path):
            return False
        
        if not self._validate_output_dir(output_path):
            return False
        
        return self._execute_with_benchmark(
            f"распаковка {archive_path.name}",
            lambda: self._decompress(archive_path, output_path)
        )
    
    def _validate_source(self, source_path: Path) -> bool:
        if not source_path.exists():
            print(f"Ошибка: '{source_path}' не существует")
            return False
        return True
    
    def _validate_output_format(self, output_path: Path) -> bool:
        
        if output_path.suffix not in self.SUPPORTED_FORMATS:
            print(f"Ошибка: неподдерживаемый формат '{output_path.suffix}'. "
                  f"Поддерживаемые форматы: {', '.join(self.SUPPORTED_FORMATS)}")
            return False
        return True
    
    def _validate_output_dir(self, output_path: Path) -> bool:
        if not output_path.exists():
            print(f"Ошибка: директория '{output_path}' не существует")
            return False
        return True
    
    def _execute_with_benchmark(self, operation: str, func: callable) -> bool:
        if self.benchmark_mode:
            start_time = time.time()
        
        try:
            func()
            success = True
        except Exception as e:
            print(f"Ошибка при выполнении {operation}: {e}")
            success = False
        
        if self.benchmark_mode:
            end_time = time.time()
            print(f"\n Время, затраченное на {operation}: "
                  f"{end_time - start_time:.4f} секунд")
        
        return success
    
    def _compress(self, source: Path, output: Path) -> None:
       
        compressors = {
            '.zstd': self._compress_zstd,
            '.bz2': self._compress_bz2
        }
        
        compressor = compressors.get(output.suffix)
        if compressor:
            compressor(source, output)
        else:
            print(f"Неподдерживаемый формат сжатия: {output.suffix}")
    
    def _decompress(self, archive: Path, output: Path) -> None:
        
        decompressors = {
            '.zstd': self._decompress_zstd,
            '.bz2': self._decompress_bz2
        }
        
        decompressor = decompressors.get(archive.suffix)
        if decompressor:
            decompressor(archive, output)
        else:
            print(f"Неподдерживаемый формат архива: {archive.suffix}")
    
    def _create_tar_for_directory(self, source: Path) -> str:
   
        temp_tar = source.name + '.temp.tar'
        with tarfile.open(temp_tar, 'w') as tar:
            tar.add(source, arcname=source.name)
        return temp_tar
    
    def _cleanup_temp_file(self, file_path: Union[str, Path]) -> None:
       
        path = Path(file_path)
        if path.exists():
            path.unlink()
    
    def _compress_zstd(self, source: Path, output: Path) -> None:
        
        temp_tar = None
        try:
            if source.is_dir():
                temp_tar = self._create_tar_for_directory(source)
                input_file = temp_tar
            else:
                input_file = source
            
            with open(input_file, 'rb') as f_in, zstd.open(output, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            
            print(f"Zstandard сжатие завершено: {output}")
        
        finally:
            if temp_tar:
                self._cleanup_temp_file(temp_tar)
    
    def _compress_bz2(self, source: Path, output: Path) -> None:
        
        temp_tar = None
        try:
            if source.is_dir():
                temp_tar = self._create_tar_for_directory(source)
                input_file = temp_tar
            else:
                input_file = source
            
            with open(input_file, 'rb') as f_in, bz2.open(output, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            
            print(f"BZ2 сжатие завершено: {output}")
        
        finally:
            if temp_tar:
                self._cleanup_temp_file(temp_tar)
    
    def _decompress_zstd(self, archive: Path, output: Path) -> None:
        
        self._decompress_with_format(archive, output, zstd.open)
    
    def _decompress_bz2(self, archive: Path, output: Path) -> None:
    
        self._decompress_with_format(archive, output, bz2.open)
    
    def _decompress_with_format(self, archive: Path, output: Path, 
                               opener: callable) -> None:
        
        temp_file = output / (archive.stem + self.TEMP_EXTENSION)
        
        try:
            with opener(archive, 'rb') as f_in, open(temp_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
            
            if self._extract_as_tar(temp_file, output):
                print(f"Распаковано как tar-архив: {archive} -> {output}")
            else:
                final_file = output / archive.stem
                shutil.move(temp_file, final_file)
                print(f"Распаковано как одиночный файл: {archive} -> {final_file}")
                temp_file = None  
        
        finally:
            if temp_file and temp_file.exists():
                self._cleanup_temp_file(temp_file)
    
    def _extract_as_tar(self, tar_path: Path, output: Path) -> bool:
        
        try:
            with tarfile.open(tar_path, 'r') as tar:
                tar.extractall(output)
            return True
        except tarfile.ReadError:
            return False


def main():
   
    parser = argparse.ArgumentParser(
        description='Архиватор Zstandard и BZ2.'
    )
    
    parser.add_argument('-b', '--benchmark', action='store_true',
                       help='Включить режим замера времени')
    
    subparsers = parser.add_subparsers(dest='command', 
                                      help='Доступные команды')
    
    create_parser = subparsers.add_parser('create', 
                                         help='Создать архив')
    create_parser.add_argument('source', 
                              help='Исходный файл или директория для архивации')
    create_parser.add_argument('output', 
                              help='Выходной файл архива (с расширением .zstd или .bz2)')
    
    extract_parser = subparsers.add_parser('extract', 
                                          help='Распаковать архив')
    extract_parser.add_argument('archive', 
                               help='Файл архива для распаковки')
    extract_parser.add_argument('output', 
                               help='Директория для распаковки')
    
    args = parser.parse_args()
    
    processor = ArchiveProcessor(benchmark_mode=args.benchmark)
    
    if args.command == 'create':
        processor.create_archive(args.source, args.output)
    elif args.command == 'extract':
        processor.extract_archive(args.archive, args.output)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()